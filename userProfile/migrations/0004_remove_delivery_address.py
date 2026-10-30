from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('userProfile', '0003_address')]

    operations = [migrations.DeleteModel(name='Address')]
