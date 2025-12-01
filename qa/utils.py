from django.db.models import Q
from community.models import Community, CommunityMember

def filter_questions_by_community_access(queryset, user):
    """
    Filter questions based on community access:
    - Show all questions not in any community
    - Show questions from public communities
    - Only show questions from private communities if user is a member
    """
    if user.is_authenticated:
        # Get IDs of private communities the user is a member of
        user_community_ids = CommunityMember.objects.filter(
            user=user, 
            is_active=True,
            community__is_private=True
        ).values_list('community_id', flat=True)
        
        # Filter: (no community) OR (public community) OR (private community where user is member)
        return queryset.filter(
            Q(community__isnull=True) |
            Q(community__is_private=False) |
            Q(community_id__in=user_community_ids)
        )
    else:
        # For anonymous users, only show questions not in any community or in public communities
        return queryset.filter(
            Q(community__isnull=True) | 
            Q(community__is_private=False)
        )