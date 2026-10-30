from django.db import migrations, models


def preserve_staff_access(apps, schema_editor):
    User = apps.get_model('users', 'User')
    User.objects.using(schema_editor.connection.alias).filter(
        models.Q(is_admin=True) | models.Q(is_superuser=True),
    ).update(is_staff=True)


class Migration(migrations.Migration):
    dependencies = [('users', '0013_user_groups_user_user_permissions')]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(
                default=False,
                help_text='Allows this user to sign in to the admin dashboard. Groups and permissions control access to features.',
            ),
        ),
        migrations.RunPython(preserve_staff_access, migrations.RunPython.noop),
    ]
