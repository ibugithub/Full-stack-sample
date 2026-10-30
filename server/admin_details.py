"""Shared details-first navigation for registered admin models."""

from urllib.parse import urlsplit

from cloudinary.models import CloudinaryField
from django import forms
from django.contrib.admin.helpers import AdminReadonlyField
from django.contrib.admin.utils import flatten, quote, unquote
from django.core.exceptions import FieldDoesNotExist, PermissionDenied
from django.db import models
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse


def image_url(field, value):
    if not value:
        return None
    if isinstance(field, CloudinaryField):
        return value.build_url(
            secure=True, width=900, crop='limit', quality='auto', fetch_format='auto',
        )
    if isinstance(field, models.ImageField):
        return value.url
    if any(word in field.name.lower() for word in ('image', 'photo', 'picture', 'avatar')):
        url = str(value)
        if urlsplit(url).scheme in ('http', 'https'):
            return url
    return None


def detail_fields(model_admin, obj, names):
    # A field-free form provides Django's readonly formatting without edit widgets.
    form_class = forms.modelform_factory(type(obj), fields=[])
    form = form_class(instance=obj)
    fields = []
    images = []
    for name in names:
        field_name = name if isinstance(name, str) else name.__name__
        # Never expose password hashes or credential material in record previews.
        if any(word in field_name.lower() for word in ('password', 'token', 'secret', 'api_key')):
            continue
        try:
            model_field = obj._meta.get_field(field_name)
        except FieldDoesNotExist:
            model_field = None
        if model_field:
            url = image_url(model_field, getattr(obj, field_name))
            if url or isinstance(model_field, (models.ImageField, CloudinaryField)):
                initials = ''.join(word[0] for word in str(obj).split()[:2]).upper()
                images.append({
                    'url': url,
                    'label': str(model_field.verbose_name).replace('_', ' '),
                    'initials': initials or 'U',
                })
                continue
        readonly = AdminReadonlyField(form, name, False, model_admin)
        fields.append({
            'label': readonly.field['label'],
            'value': readonly.contents(),
            'wide': isinstance(model_field, (models.TextField, models.JSONField)),
        })
    return fields, images


def record_details(
    model_admin, request, object_id, extra_context=None,
    editor_context=None, editing=False, resolved_object=None,
):
    opts = model_admin.model._meta
    obj = resolved_object if resolved_object is not None else model_admin.get_object(request, unquote(object_id))
    if obj is None:
        return model_admin._get_obj_does_not_exist_redirect(request, opts, object_id)
    if not model_admin.has_view_or_change_permission(request, obj):
        raise PermissionDenied

    sections = []
    images = []
    direct_section = getattr(model_admin, 'details_form_section', None)
    follow_up_form = editor_context['adminform'].form if direct_section and editor_context and model_admin.has_change_permission(request, obj) else None
    fieldsets = model_admin.get_fieldsets(request, obj)
    for title, options in fieldsets:
        names = flatten(options['fields'])
        show_form = follow_up_form is not None and title == direct_section
        if show_form:
            names = [name for name in names if name not in follow_up_form.fields]
        fields, section_images = detail_fields(model_admin, obj, names)
        images.extend(section_images)
        if fields or show_form:
            sections.append({'title': title or 'Details', 'fields': fields, 'follow_up': show_form})

    related_sections = []
    for inline in model_admin.get_inline_instances(request, obj):
        if not inline.has_view_or_change_permission(request, obj):
            continue
        formset = inline.get_formset(request, obj)
        queryset = inline.get_queryset(request).filter(**{formset.fk.name: obj})
        names = [
            name for name in flatten([options['fields'] for _, options in inline.get_fieldsets(request, obj)])
            if name != formset.fk.name
        ]
        records = []
        limit = getattr(inline, 'details_limit', 25)
        for related in queryset[:limit + 1]:
            fields, related_images = detail_fields(inline, related, names)
            records.append({'name': str(related), 'fields': fields, 'images': related_images, 'original': related})
        empty_message = getattr(inline, 'details_empty_message', None)
        if records or empty_message:
            related_sections.append({
                'title': inline.verbose_name_plural,
                'records': records[:limit],
                'truncated': len(records) > limit,
                'limit': limit,
                'empty_message': empty_message,
                'template': getattr(inline, 'details_template', None),
            })

    context = {
        **model_admin.admin_site.each_context(request),
        'opts': opts,
        'original': obj,
        'title': str(obj),
        'sections': sections,
        'images': images,
        'related_sections': related_sections,
        'can_edit': model_admin.has_change_permission(request, obj) and not direct_section,
        'editor': editor_context if not direct_section else None,
        'follow_up_form': follow_up_form,
        'follow_up_template': getattr(model_admin, 'details_follow_up_template', 'admin/includes/record_follow_up.html'),
        'direct_follow_up': bool(direct_section),
        'editing': editing and not direct_section,
        'history_url': reverse(
            f'{model_admin.admin_site.name}:{opts.app_label}_{opts.model_name}_history',
            args=[quote(obj.pk)],
        ),
        'changelist_url': reverse(
            f'{model_admin.admin_site.name}:{opts.app_label}_{opts.model_name}_changelist',
        ),
        'delete_url': reverse(
            f'{model_admin.admin_site.name}:{opts.app_label}_{opts.model_name}_delete',
            args=[quote(obj.pk)],
        ),
        'preserved_filters': model_admin.get_preserved_filters(request),
        **(extra_context or {}),
    }
    request.current_app = model_admin.admin_site.name
    return TemplateResponse(request, 'admin/object_details.html', context)


def enable_record_details(model_admin):
    if getattr(model_admin, '_app_details_enabled', False):
        return
    original_change_view = model_admin.change_view

    def change_view(request, object_id, form_url='', extra_context=None):
        # Popups keep their native flow; all mutations still use Django validation.
        if '_popup' in request.GET or '_popup' in request.POST:
            return original_change_view(request, object_id, form_url, extra_context)
        if request.method == 'GET':
            response = original_change_view(request, object_id, form_url, extra_context)
            if response.status_code != 200 or not hasattr(response, 'context_data'):
                return response
            context = response.context_data
            return record_details(
                model_admin, request, object_id, extra_context,
                editor_context=context if context['has_change_permission'] else None,
                editing=request.GET.get('edit') == '1',
                resolved_object=context['original'],
            )
        response = original_change_view(request, object_id, form_url, extra_context)
        if request.method == 'POST':
            if response.status_code == 200 and hasattr(response, 'context_data'):
                return record_details(
                    model_admin, request, object_id, extra_context,
                    editor_context=response.context_data, editing=True,
                )
            if response.status_code == 302 and '_save' in request.POST and '_saveasnew' not in request.POST:
                query = request.GET.copy()
                query.pop('edit', None)
                suffix = f'?{query.urlencode()}' if query else ''
                anchor = '#record-followup' if getattr(model_admin, 'details_form_section', None) else ''
                return HttpResponseRedirect(f'{request.path}{suffix}{anchor}')
        return response

    model_admin.change_view = change_view
    model_admin._app_details_enabled = True
