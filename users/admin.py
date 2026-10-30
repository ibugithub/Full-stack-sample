from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.db.models import Q
from userProfile.models import Profile
from .models import CustomPermissionGroup, User
from .forms import EffectiveUserPermissionsForm
from .permission_roles import synchronize_permission_groups
from .widgets import MemberPicker, PermissionPicker


def dashboard_permissions(queryset, request, site):
    """Offer only permissions backed by an available admin action."""
    available = Q(pk__in=[])
    for model, model_admin in site._registry.items():
        actions = [
            f'{action}_{model._meta.model_name}'
            for action in ('view', 'add', 'change', 'delete')
            if getattr(model_admin, f'has_{action}_permission')(request)
        ]
        available |= Q(
            content_type__app_label=model._meta.app_label,
            content_type__model=model._meta.model_name,
            codename__in=actions,
        )
    return queryset.filter(available).select_related('content_type')


class UserDetailsPermissions:
    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('users.view_user') or request.user.has_perm('users.change_user')

    def has_change_permission(self, request, obj=None):
        return self.admin_site._registry[User].has_change_permission(request, obj)

    def has_add_permission(self, request, obj=None):
        parent = self.admin_site._registry[User]
        return parent.has_change_permission(request, obj) if obj else parent.has_add_permission(request)


class UserProfileInline(UserDetailsPermissions, admin.StackedInline):
    model = Profile
    verbose_name = 'Additional details'
    verbose_name_plural = 'Additional details'
    fields = ('Display_name', 'profile_picture', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    extra = 0
    max_num = 1
    can_delete = False

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 1
        try:
            obj.profile
        except Profile.DoesNotExist:
            return 1
        return 0



class UserAdmin(BaseUserAdmin):
    form = EffectiveUserPermissionsForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'user_permissions' in form.base_fields:
            widget = form.base_fields['user_permissions'].widget
            while hasattr(widget, 'widget'):
                widget = widget.widget
            widget.superuser_field = 'id_is_superuser'
            widget.effective_superuser = bool(obj and obj.is_superuser)
            widget.effective_editor = True
        return form

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == 'user_permissions' and field:
            field.queryset = dashboard_permissions(field.queryset, request, self.admin_site)
            field.widget = PermissionPicker(choices=field.choices)
            field.help_text = 'Selected permissions include group and individual access. Saving matches complete groups and puts remaining permissions into a Custom group.'
        return field

    list_display = ('email', 'name', 'signUp_by', 'is_staff', 'is_superuser', 'is_verified')
    list_filter = ('is_staff', 'groups')
    readonly_fields = ('id', 'first_name', 'last_name', 'sign_in_method', 'last_login', 'groups')
    inlines = (UserProfileInline,)
    fieldsets = (
        ('Account', {'fields': ('id', 'email', 'password', 'sign_in_method')}),
        ('Personal info', {'fields': ('name', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_verified', 'is_superuser', 'groups', 'user_permissions')}),
        ('Account activity', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'name', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            return (*fields, 'is_staff', 'is_superuser', 'user_permissions')
        return fields

    def has_change_permission(self, request, obj=None):
        if obj and not request.user.is_superuser and (obj.is_staff or obj.is_superuser):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and not request.user.is_superuser and (obj.is_staff or obj.is_superuser):
            return False
        return super().has_delete_permission(request, obj)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')

    @admin.display(description='Sign-in method')
    def sign_in_method(self, obj):
        return dict(User.SIGNUP_METHODS).get(obj.signUp_by.strip().lower(), 'Not recorded')


    def save_model(self, request, obj, form, change):
        if not change or 'name' in form.changed_data:
            parts = obj.name.strip().split(maxsplit=1)
            obj.first_name = parts[0] if parts else ''
            obj.last_name = parts[1] if len(parts) > 1 else ''
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if request.user.is_superuser and 'user_permissions' in form.cleaned_data and not form.instance.is_superuser:
            synchronize_permission_groups(
                form.instance, {permission.pk for permission in form.cleaned_data['user_permissions']},
            )

# Register the new UserAdmin
admin.site.register(User, UserAdmin)


class GroupMembersForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.order_by('email'), required=False,
        widget=MemberPicker(),
        help_text='Select the users who should inherit these permissions. Admin access also requires staff access on their User record.',
    )

    class Meta:
        model = Group
        fields = ('name', 'permissions', 'members')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and 'permissions' in self.fields:
            field = self.fields['permissions']
            field.queryset = field.queryset.model.objects.filter(
                Q(pk__in=field.queryset.values('pk'))
                | Q(pk__in=self.instance.permissions.values('pk')),
            ).distinct().select_related('content_type')
        if self.instance.pk and 'members' in self.fields:
            self.fields['members'].initial = self.instance.user_set.all()

    def clean_members(self):
        members = self.cleaned_data['members']
        if self.instance.pk:
            custom = CustomPermissionGroup.objects.filter(group=self.instance).first()
            if custom and set(members.values_list('pk', flat=True)) != ({custom.owner_id} if custom.owner_id else set()):
                raise forms.ValidationError('This Custom group belongs to one user. Change its permissions from that user’s Effective permissions section.')
        return members


class GroupAdmin(BaseGroupAdmin):
    form = GroupMembersForm

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == 'permissions' and field:
            field.queryset = dashboard_permissions(field.queryset, request, self.admin_site)
            field.widget = PermissionPicker(choices=field.choices)
            field.help_text = 'Members inherit all selected permissions.'
        return field

    @admin.display(description='Members')
    def members(self, obj):
        return ', '.join(obj.user_set.order_by('email').values_list('email', flat=True))

    def has_add_permission(self, request):
        return request.user.is_superuser and super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser and super().has_delete_permission(request, obj)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.user_set.set(form.cleaned_data['members'])


admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
