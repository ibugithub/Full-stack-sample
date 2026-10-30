from django import forms


class RecordFileInput(forms.ClearableFileInput):
    template_name = 'admin/widgets/record_file.html'


class PermissionPicker(forms.SelectMultiple):
    template_name = 'admin/widgets/permission_picker.html'
    superuser_field = None
    effective_superuser = False
    effective_editor = False

    class Media:
        css = {'all': ('admin/css/permission_picker.css',)}
        js = ('admin/js/permission_picker.js',)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['superuser_field'] = self.superuser_field
        context['effective_superuser'] = self.effective_superuser
        context['effective_editor'] = self.effective_editor
        features = {}
        for _, options, _ in context['widget']['optgroups']:
            for option in options:
                permission = option['value'].instance
                content_type = permission.content_type
                model = content_type.model_class()
                feature = str(model._meta.verbose_name_plural) if model else content_type.model
                app = model._meta.app_config.verbose_name if model else content_type.app_label
                key = (str(app), feature)
                group = features.setdefault(key, {'app': app, 'name': feature, 'options': []})
                action = permission.codename.split('_', 1)[0]
                option['action'] = {
                    'view': 'View', 'add': 'Add', 'change': 'Edit', 'delete': 'Delete',
                }.get(action, permission.name)
                group['options'].append(option)
        context['features'] = [features[key] for key in sorted(features)]
        for feature in context['features']:
            feature['options'].sort(key=lambda option: {
                'View': 0, 'Add': 1, 'Edit': 2, 'Delete': 3,
            }.get(option['action'], 4))
            feature['cells'] = [
                {'action': action, 'option': next((option for option in feature['options'] if option['action'] == action), None)}
                for action in ('View', 'Add', 'Edit', 'Delete')
            ]
        return context


class MemberPicker(forms.SelectMultiple):
    template_name = 'admin/widgets/member_picker.html'

    class Media(PermissionPicker.Media):
        pass
