from django import template

register = template.Library()

@register.filter
def is_teacher_verified(user):
    """Check if user is a verified teacher with @khwopa.edu.np email"""
    if hasattr(user, 'profile'):
        return (user.profile.user_type == 'Teacher' and 
                user.profile.is_verified and 
                user.email.endswith('@khwopa.edu.np'))
    return False

@register.inclusion_tag('profile/verification_badge.html')
def show_verification_badge(user):
    """Display verification badge for verified teachers"""
    is_verified = False
    if hasattr(user, 'profile'):
        is_verified = (user.profile.user_type == 'Teacher' and 
                      user.profile.is_verified and 
                      user.email.endswith('@khwopa.edu.np'))
    return {'is_verified': is_verified}
