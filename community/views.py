from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from .models import Community, CommunityMember
from .forms import CommunityForm

@login_required
def community_list(request):
    """List all communities with search and filter"""
    communities = Community.objects.filter(is_active=True)
    
    # Initialize categories as empty list
    categories = []
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        from django.db.models import Q
        communities = communities.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(communities, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get user's ACTIVE joined communities only
    user_communities = []
    if request.user.is_authenticated:
        user_communities = request.user.community_memberships.filter(
            is_active=True
        ).values_list('community_id', flat=True)
    
    context = {
        'page_obj': page_obj,
        'communities': page_obj.object_list,
        'categories': categories,  # Empty list for now
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
    """Join a community - atomic operation"""
    community = get_object_or_404(Community, slug=slug, is_active=True)
    
    # Check if already an active member
    if CommunityMember.objects.filter(
        community=community, 
        user=request.user,
        is_active=True
    ).exists():
        return JsonResponse({'success': False, 'message': 'Already a member'}, status=400)
    
    # Handle re-join: reactivate if soft-deleted
    member, created = CommunityMember.objects.get_or_create(
        community=community,
        user=request.user,
        defaults={'role': 'member', 'is_active': True}
    )
    if not created and not member.is_active:
        member.is_active = True
        member.save()
    
    # Update member count
    community.member_count = community.members.filter(is_active=True).count()
    community.save()
    
    return JsonResponse({'success': True, 'message': 'Joined community successfully'})


@login_required
@require_http_methods(["POST"])
def leave_community(request, slug):
    """Leave a community - atomic operation"""
    community = get_object_or_404(Community, slug=slug, is_active=True)
    
    try:
        member = CommunityMember.objects.get(
            community=community, 
            user=request.user,
            is_active=True
        )
        
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
def edit_community(request, slug):
    """Edit community details"""
    community = get_object_or_404(Community, slug=slug, is_active=True)
    
    # Check if user is an admin of the community
    is_admin = CommunityMember.objects.filter(
        community=community,
        user=request.user,
        role='admin',
        is_active=True
    ).exists()
    
    if not is_admin and request.user != community.creator:
        messages.error(request, 'You do not have permission to edit this community')
        return redirect('community:community_detail', slug=slug)
    
    if request.method == 'POST':
        form = CommunityForm(request.POST, request.FILES, instance=community)
        if form.is_valid():
            updated_community = form.save(commit=False)
            # Only update the slug if the name has changed
            if 'name' in form.changed_data:
                from django.utils.text import slugify
                updated_community.slug = slugify(form.cleaned_data['name'])
            updated_community.save()
            messages.success(request, 'Community updated successfully')
            return redirect('community:community_detail', slug=updated_community.slug)
    else:
        form = CommunityForm(instance=community)
    
    context = {
        'form': form,
        'community': community,
        'is_admin': is_admin,
    }
    return render(request, 'community/edit_community.html', context)


@login_required
def community_members(request, slug):
    """View community members"""
    community = get_object_or_404(Community, slug=slug, is_active=True)
    
    # Check if user is a member if community is private
    if community.is_private and not request.user.is_authenticated:
        return redirect('account_login') + f'?next={request.path}'
    
    if community.is_private and request.user.is_authenticated:
        is_member = CommunityMember.objects.filter(
            community=community,
            user=request.user,
            is_active=True
        ).exists()
        if not is_member and request.user != community.creator:
            messages.error(request, 'This is a private community. You need to be a member to view its members.')
            return redirect('community:community_list')
    
    # Get all active members with user profile
    members = CommunityMember.objects.filter(
        community=community,
        is_active=True
    ).select_related('user', 'user__profile')
    
    # Check if current user is admin or creator
    is_admin_or_creator = (request.user == community.creator or 
                          CommunityMember.objects.filter(
                              community=community,
                              user=request.user,
                              role='admin',
                              is_active=True
                          ).exists())
    
    # Pagination
    paginator = Paginator(members, 20)  # Show 20 members per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'community': community,
        'members': page_obj,
        'page_obj': page_obj,
        'is_admin_or_creator': is_admin_or_creator,
    }
    return render(request, 'community/community_members.html', context)


@login_required
@require_POST
def remove_member(request, slug, user_id):
    """Remove a member from the community"""
    community = get_object_or_404(Community, slug=slug, is_active=True)
    user_to_remove = get_object_or_404(User, id=user_id)
    
    # Check if the current user is the community creator or an admin
    is_creator = request.user == community.creator
    is_admin = CommunityMember.objects.filter(
        community=community,
        user=request.user,
        role='admin',
        is_active=True
    ).exists()
    
    if not (is_creator or is_admin):
        messages.error(request, 'You do not have permission to remove members')
        return redirect('community:community_detail', slug=slug)
    
    # Prevent removing the community creator
    if user_to_remove == community.creator:
        messages.error(request, 'Cannot remove the community creator')
        return redirect('community:community_members', slug=slug)
    
    # Get the member to remove
    member = get_object_or_404(
        CommunityMember,
        community=community,
        user=user_to_remove,
        is_active=True
    )
    
    # Check if removing the last admin
    if member.role == 'admin':
        admin_count = CommunityMember.objects.filter(
            community=community,
            role='admin',
            is_active=True
        ).count()
        if admin_count <= 1:
            messages.error(request, 'Cannot remove the last admin. Please assign another admin first.')
            return redirect('community:community_members', slug=slug)
    
    # Deactivate the member
    member.is_active = False
    member.save()
    
    # Update member count
    community.member_count = CommunityMember.objects.filter(
        community=community,
        is_active=True
    ).count()
    community.save()
    
    messages.success(request, f'Member {user_to_remove.username} has been removed from the community')
    return redirect('community:community_members', slug=slug)


@login_required
@require_POST
def change_member_role(request, slug, user_id):
    """Change a member's role in the community"""
    community = get_object_or_404(Community, slug=slug, is_active=True)
    user = get_object_or_404(User, id=user_id)
    
    # Check if the current user is the community creator or an admin
    is_creator = request.user == community.creator
    is_admin = CommunityMember.objects.filter(
        community=community,
        user=request.user,
        role='admin',
        is_active=True
    ).exists()
    
    if not (is_creator or is_admin):
        messages.error(request, 'You do not have permission to change member roles')
        return redirect('community:community_detail', slug=slug)
    
    # Get the member to update
    member = get_object_or_404(
        CommunityMember,
        community=community,
        user=user,
        is_active=True
    )
    
    # Get the new role from the form
    new_role = request.POST.get('role')
    if new_role not in ['admin', 'moderator', 'member']:
        messages.error(request, 'Invalid role specified')
        return redirect('community:community_members', slug=slug)
    
    # Update the role
    member.role = new_role
    member.save()
    
    messages.success(request, f'Updated role for {user.username} to {new_role}')
    return redirect('community:community_members', slug=slug)
