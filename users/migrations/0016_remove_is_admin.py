from django.db import migrations, models


def preserve_legacy_access(apps, schema_editor):
    User = apps.get_model('users', 'User')
    User.objects.using(schema_editor.connection.alias).filter(
        models.Q(is_admin=True) | models.Q(is_superuser=True), is_staff=False,
    ).update(is_staff=True)


class Migration(migrations.Migration):
    dependencies = [('users', '0015_custompermissiongroup')]

    operations = [
        migrations.RunPython(preserve_legacy_access, migrations.RunPython.noop),
        migrations.RemoveField(model_name='user', name='is_admin'),
    ]
