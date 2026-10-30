from django.db import migrations, models


def populate_names(apps, schema_editor):
    User = apps.get_model('users', 'User')
    database = schema_editor.connection.alias
    batch = []
    for user in User.objects.using(database).only('pk', 'name').iterator(chunk_size=500):
        parts = user.name.strip().split(maxsplit=1)
        user.first_name = parts[0] if parts else ''
        user.last_name = parts[1] if len(parts) > 1 else ''
        batch.append(user)
        if len(batch) == 500:
            User.objects.using(database).bulk_update(batch, ['first_name', 'last_name'])
            batch = []
    if batch:
        User.objects.using(database).bulk_update(batch, ['first_name', 'last_name'])


class Migration(migrations.Migration):
    dependencies = [('users', '0011_user_signup_by')]

    operations = [
        migrations.AddField(
            model_name='user', name='first_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='user', name='last_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.RunPython(populate_names, migrations.RunPython.noop),
    ]
