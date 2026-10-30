from types import MethodType
from cloudinary.models import CloudinaryField
from django import forms
from django.contrib.admin import ShowFacets
from django.urls import path, reverse
from .admin_details import enable_record_details
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from users.widgets import RecordFileInput
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from users.admin_google import google_admin_login
from users.google import google_configured


ACCOUNT_APP_LABELS = {'auth', 'users', 'userProfile', 'userprofile'}
ACCOUNT_MODEL_ORDER = {
    'User': 1,
    'Profile': 2,
    'Group': 3,
}
APP_ORDER = {
    'accounts': 1,
}


def configure_model_admin(model_admin):
    """Shared presentation and list limits for existing and future models."""
    model_admin.change_list_template = 'admin/modern_change_list.html'
    if not model_admin.search_help_text:
        model_admin.search_help_text = f'Search {model_admin.model._meta.verbose_name_plural.lower()}'
    model_admin.list_per_page = 25
    model_admin.list_max_show_all = 25
    model_admin.show_full_result_count = False
    model_admin.show_facets = ShowFacets.NEVER
    if not getattr(model_admin, '_app_file_widget_enabled', False):
        original_formfield = model_admin.formfield_for_dbfield

        def formfield_for_dbfield(db_field, request, **kwargs):
            field = original_formfield(db_field, request, **kwargs)
            if isinstance(db_field, CloudinaryField) and field is not None and isinstance(field.widget, forms.ClearableFileInput):
                field.widget = RecordFileInput(attrs=dict(field.widget.attrs))
                field.label = str(field.label).replace('_', ' ')
            return field

        model_admin.formfield_for_dbfield = formfield_for_dbfield
        model_admin._app_file_widget_enabled = True
    enable_record_details(model_admin)


def configure_admin_site(site):
    # Token records support logout internally; they are not management features.
    for model in (BlacklistedToken, OutstandingToken):
        if site.is_registered(model):
            site.unregister(model)

    for model_admin in site._registry.values():
        configure_model_admin(model_admin)

    if getattr(site, '_template_grouped_app_list', False):
        return

    original_get_app_list = site.get_app_list
    original_get_urls = site.get_urls
    original_register = site.register
    original_login = site.login

    def login(self, request, extra_context=None):
        context = {
            'google_admin_enabled': google_configured(),
            'google_admin_login_url': reverse(f'{self.name}:google-login'),
            **(extra_context or {}),
        }
        return original_login(request, extra_context=context)

    site.login = MethodType(login, site)

    def register(self, model_or_iterable, admin_class=None, **options):
        existing_models = set(self._registry)
        result = original_register(model_or_iterable, admin_class, **options)
        for model in self._registry.keys() - existing_models:
            configure_model_admin(self._registry[model])
        return result

    site.register = MethodType(register, site)

    def get_grouped_app_list(self, request, app_label=None):
        if app_label == 'accounts':
            return [
                app for app in get_grouped_app_list(self, request)
                if app['app_label'] == 'accounts'
            ]

        app_list = original_get_app_list(request, app_label)

        if app_label is not None:
            return app_list

        account_models = []
        has_account_permissions = False
        grouped_apps = []

        for app in app_list:
            if app['app_label'] in ACCOUNT_APP_LABELS:
                account_models.extend(app['models'])
                has_account_permissions = has_account_permissions or app.get('has_module_perms', False)
                continue
            grouped_apps.append(app)

        if account_models:
            account_models.sort(
                key=lambda model: (
                    ACCOUNT_MODEL_ORDER.get(model.get('object_name'), 100),
                    model['name'].lower(),
                )
            )
            grouped_apps.append({
                'name': 'Accounts',
                'app_label': 'accounts',
                'app_url': reverse(f'{self.name}:accounts'),
                'has_module_perms': has_account_permissions,
                'models': account_models,
            })

        grouped_apps.sort(key=lambda app: (APP_ORDER.get(app['app_label'], 100), app['name'].lower()))
        return grouped_apps

    site.get_app_list = MethodType(get_grouped_app_list, site)

    def accounts_view(request):
        return site.app_index(request, 'accounts')

    @require_GET
    def dashboard_counts(request):
        counts = {}
        for model, model_admin in site._registry.items():
            if model_admin.has_module_permission(request) and model_admin.has_view_permission(request):
                url = reverse(f'{site.name}:{model._meta.app_label}_{model._meta.model_name}_changelist')
                counts[url] = {'value': model_admin.get_queryset(request).count(), 'label': 'total'}
        response = JsonResponse({'counts': counts})
        response['Cache-Control'] = 'private, no-store'
        return response

    def get_urls(self):
        return [
            path('google/login/', google_admin_login, name='google-login'),
            path('dashboard-counts/', self.admin_view(dashboard_counts), name='dashboard-counts'),
            path('accounts/', self.admin_view(accounts_view), name='accounts'),
            *original_get_urls(),
        ]

    site.get_urls = MethodType(get_urls, site)
    site._template_grouped_app_list = True
