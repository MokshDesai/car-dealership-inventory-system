from django.db import migrations

def create_admin_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    if not User.objects.filter(username='admin').exists():
        # create_superuser sets both is_staff=True and is_superuser=True
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )

def remove_admin_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='admin').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin_user, reverse_code=remove_admin_user),
    ]
