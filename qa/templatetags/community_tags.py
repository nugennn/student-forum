from django import template
from community.models import CommunityMember

register = template.Library()

@register.filter
def is_community_member(user, community):
    if not user.is_authenticated:
        return False
    return CommunityMember.objects.filter(
        user=user,
        community=community,
        is_active=True
    ).exists()

@register.filter
def can_view_community_question(user, question):
    if not question.community:
        return True
    if not question.community.is_private:
        return True
    if not user.is_authenticated:
        return False
    return CommunityMember.objects.filter(
        user=user,
        community=question.community,
        is_active=True
    ).exists()
