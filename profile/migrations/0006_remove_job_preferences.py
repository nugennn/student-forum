from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0005_profile_is_verified_profile_user_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='job_search_status',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='job_type',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='max_expierence_level',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='min_expierence_level',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='phone_number',
        ),
    ]
