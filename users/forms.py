from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import Permission
from django.db.models import Q

from .models import User


class EffectiveUserPermissionsForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.fields.get('user_permissions')
        if field is not None:
            if self.instance.pk:
                inherited = Permission.objects.filter(
                    Q(user=self.instance) | Q(group__user=self.instance),
                ).values_list('pk', flat=True)
                field.queryset = Permission.objects.filter(
                    Q(pk__in=field.queryset.values('pk')) | Q(pk__in=inherited),
                ).distinct().select_related('content_type')
                selected = field.queryset.values_list('pk', flat=True) if self.instance.is_superuser else inherited
                self.initial['user_permissions'] = list(selected)
            field.label = 'Effective permissions'
            field.help_text = 'All selected access is saved through complete matching groups and a user-specific Custom group for remaining permissions. Unchecking a permission removes that access.'

    def clean(self):
        cleaned = super().clean()
        if 'user_permissions' in cleaned and cleaned.get('is_superuser'):
            selected = {permission.pk for permission in cleaned['user_permissions']}
            available = set(self.fields['user_permissions'].queryset.values_list('pk', flat=True))
            if selected != available:
                # A superuser bypass would otherwise keep unchecked access active.
                cleaned['is_superuser'] = False
        return cleaned

    def _save_m2m(self):
        # The admin reconciles effective selections into groups after native saving.
        selected = self.cleaned_data.pop('user_permissions', None)
        try:
            super()._save_m2m()
        finally:
            if selected is not None:
                self.cleaned_data['user_permissions'] = selected
