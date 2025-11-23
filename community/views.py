from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Community, CommunityMember, CommunityCategory
from .forms import CommunityForm


@login_required
def community_list(request):
    """List all communities with search and filter"""
    communities = Community.objects.filter(is_active=True)
    categories = CommunityCategory.objects.all()
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        communities = communities.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Filter by category
    category_slug = request.GET.get('category', '')
    if category_slug:
        category = get_object_or_404(CommunityCategory, slug=category_slug)
        # You can add a category field to Community model later
    
    # Pagination
    paginator = Paginator(communities, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get user's joined communities
    user_communities = request.user.community_memberships.values_list('community_id', flat=True)
    
    context = {
        'page_obj': page_obj,
        'communities': page_obj.object_list,
        'categories': categories,
        'search_query': search_query,
        'user_communities': user_communities,
    }
    return render(request, 'community/community_list.html', context)


@login_required
def community_detail(request, slug):
    """View community details and preview"""
    community = get_object_or_404(Community, slug=slug, is_active=True)
    
    # Check if user is a member
    is_member = CommunityMember.objects.filter(
        community=community, 
        user=request.user,
        is_active=True
    ).exists()
    
    # Get member role if user is a member
    member_role = None
    if is_member:
        member = CommunityMember.objects.get(community=community, user=request.user)
        member_role = member.role
    
    # Get community members
    members = community.members.filter(is_active=True).select_related('user')[:10]
    
    context = {
        'community': community,
        'is_member': is_member,
        'member_role': member_role,
        'members': members,
        'member_count': community.member_count,
    }
    return render(request, 'community/community_detail.html', context)


@login_required
def create_community(request):
    """Create a new community"""
    if request.method == 'POST':
        form = CommunityForm(request.POST, request.FILES)
        if form.is_valid():
            community = form.save(commit=False)
            community.creator = request.user
            community.save()
            
            # Add creator as admin
            CommunityMember.objects.create(
                community=community,
                user=request.user,
                role='admin'
            )
            community.member_count = 1
            community.save()
            
            messages.success(request, f'Community "{community.name}" created successfully!')
            return redirect('community:community_detail', slug=community.slug)
    else:
        form = CommunityForm()
    
    context = {'form': form}
    return render(request, 'community/create_community.html', context)


@login_required
@require_http_methods(["POST"])
def join_community(request, slug):
    """Join a community"""
    community = get_object_or_404(Community, slug=slug, is_active=True)
    
    # Check if already a member
    if CommunityMember.objects.filter(community=community, user=request.user).exists():
        return JsonResponse({'success': False, 'message': 'Already a member'}, status=400)
    
    # Create membership
    CommunityMember.objects.create(
        community=community,
        user=request.user,
        role='member'
    )
    
    # Update member count
    community.member_count = community.members.filter(is_active=True).count()
    community.save()
    
    messages.success(request, f'You joined {community.name}!')
    return JsonResponse({'success': True, 'message': 'Joined community successfully'})


@login_required
@require_http_methods(["POST"])
def leave_community(request, slug):
    """Leave a community"""
    community = get_object_or_404(Community, slug=slug, is_active=True)
    
    try:
        member = CommunityMember.objects.get(community=community, user=request.user)
        
        # Don't allow last admin to leave
        if member.role == 'admin':
            admin_count = community.members.filter(role='admin', is_active=True).count()
            if admin_count == 1:
                return JsonResponse(
                    {'success': False, 'message': 'Cannot leave: you are the only admin'}, 
                    status=400
                )
        
        member.is_active = False
        member.save()
        
        # Update member count
        community.member_count = community.members.filter(is_active=True).count()
        community.save()
        
        messages.success(request, f'You left {community.name}')
        return JsonResponse({'success': True, 'message': 'Left community successfully'})
    
    except CommunityMember.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Not a member'}, status=400)


@login_required
def my_communities(request):
    """View user's joined communities"""
    communities = Community.objects.filter(
        members__user=request.user,
        members__is_active=True,
        is_active=True
    ).distinct()
    
    # Pagination
    paginator = Paginator(communities, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'communities': page_obj.object_list,
    }
    return render(request, 'community/my_communities.html', context)


@login_required
def community_members(request, slug):
    """View community members"""
    community = get_object_or_404(Community, slug=slug, is_active=True)
    
    # Check if user is a member
    is_member = CommunityMember.objects.filter(
        community=community,
        user=request.user,
        is_active=True
    ).exists()
    
    if not is_member:
        messages.error(request, 'You must be a member to view members')
        return redirect('community:community_detail', slug=slug)
    
    members = community.members.filter(is_active=True).select_related('user')
    
    # Pagination
    paginator = Paginator(members, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'community': community,
        'page_obj': page_obj,
        'members': page_obj.object_list,
    }
    return render(request, 'community/community_members.html', context)
