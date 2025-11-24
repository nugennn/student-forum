from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Mark all users with @khwopa.edu.np email as teachers and verify them'

    def handle(self, *args, **options):
        # Find all users with @khwopa.edu.np email
        khwopa_users = User.objects.filter(email__iendswith='@khwopa.edu.np')
        
        updated_count = 0
        already_marked = 0
        
        for user in khwopa_users:
            if hasattr(user, 'profile'):
                # Check if already marked as teacher
                if user.profile.user_type == 'Teacher' and user.profile.is_verified:
                    already_marked += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ {user.username} ({user.email}) - Already marked as Teacher')
                    )
                else:
                    # Update to teacher and verify
                    user.profile.user_type = 'Teacher'
                    user.profile.is_verified = True
                    user.profile.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Updated: {user.username} ({user.email}) → Teacher (Verified)')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ {user.username} ({user.email}) - No profile found')
                )
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'\n✅ Summary:'))
        self.stdout.write(f'   Total @khwopa.edu.np users found: {khwopa_users.count()}')
        self.stdout.write(f'   Updated to Teacher: {updated_count}')
        self.stdout.write(f'   Already marked as Teacher: {already_marked}')
        self.stdout.write('='*60 + '\n')
