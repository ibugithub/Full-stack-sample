from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('users', '0014_user_is_staff'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomPermissionGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='custom_permission_bundle', to='auth.group')),
                ('owner', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='custom_permission_bundle', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
