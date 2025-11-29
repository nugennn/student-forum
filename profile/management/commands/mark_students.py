from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from profile.models import Profile


class Command(BaseCommand):
    help = 'Mark users with @khec.edu.np email as students'

    def handle(self, *args, **options):
        # Find all users with @khec.edu.np email
        khec_users = User.objects.filter(email__endswith='@khec.edu.np')
        
        count = 0
        for user in khec_users:
            profile = user.profile
            if not profile.is_student:
                profile.is_student = True
                profile.user_type = 'Student'
                profile.is_verified = True
                profile.save()
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Marked {user.username} ({user.email}) as student')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal users marked as students: {count}')
        )
