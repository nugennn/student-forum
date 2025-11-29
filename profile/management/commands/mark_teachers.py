from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from profile.models import Profile


class Command(BaseCommand):
    help = 'Mark users with @khwopa.edu.np email as teachers'

    def handle(self, *args, **options):
        # Find all users with @khwopa.edu.np email
        khwopa_users = User.objects.filter(email__endswith='@khwopa.edu.np')
        
        count = 0
        for user in khwopa_users:
            profile = user.profile
            if not profile.is_teacher:
                profile.is_teacher = True
                profile.user_type = 'Teacher'
                profile.is_verified = True
                profile.save()
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Marked {user.username} ({user.email}) as teacher')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal users marked as teachers: {count}')
        )
