from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
import json
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from .models import PrivateChat, GroupChat, Message, MessageReaction, ChatNotification
from django.db.models import Count


def get_suggested_users(user, limit=10):
    """
    Get suggested users for messaging based on priority:
    1. Users with mutual interactions (commented on user's posts, upvoted, etc.)
    2. Recently active users (posted or logged in within last 24-48 hours)
    3. Other active users
    
    Excludes:
    - The current user
    - Users already in active chats
    - Superusers (admin accounts)
    """
    from datetime import timedelta
    from qa.models import Question, Answer, CommentQ, QUpvote
    
    # Get users already chatted with (to exclude)
    chatted_user_ids = set(
        PrivateChat.objects.filter(participants=user)
        .values_list('participants', flat=True)
    )
    chatted_user_ids.discard(user.id)  # Remove current user if present
    
    # Time thresholds for recent activity
    recent_24h = timezone.now() - timedelta(hours=24)
    recent_48h = timezone.now() - timedelta(hours=48)
    
    # Priority 1: Users with mutual interactions
    # Users who commented on current user's questions
    user_questions = Question.objects.filter(post_owner=user, is_deleted=False)
    commenters_on_my_posts = User.objects.filter(
        commentq__question_comment__in=user_questions
    ).exclude(id=user.id).exclude(id__in=chatted_user_ids).exclude(is_superuser=True).distinct()
    
    # Users who upvoted current user's questions
    upvoters_on_my_posts = User.objects.filter(
        qupvote__upvote_question_of__in=user_questions
    ).exclude(id=user.id).exclude(id__in=chatted_user_ids).exclude(is_superuser=True).distinct()
    
    # Users whose posts current user has interacted with
    my_comments = CommentQ.objects.filter(commented_by=user)
    users_i_commented_on = User.objects.filter(
        Q(question__commentq__in=my_comments) | Q(answer__commentq__in=my_comments)
    ).exclude(id=user.id).exclude(id__in=chatted_user_ids).exclude(is_superuser=True).distinct()
    
    # Combine mutual interaction users
    mutual_interaction_users = (
        commenters_on_my_posts | upvoters_on_my_posts | users_i_commented_on
    ).distinct()
    
    # Priority 2: Recently active users (24 hours)
    recently_active_24h = User.objects.filter(
        Q(last_login__gte=recent_24h) |
        Q(question__date__gte=recent_24h) |
        Q(answer__date__gte=recent_24h)
    ).exclude(id=user.id).exclude(id__in=chatted_user_ids).exclude(is_superuser=True).distinct()
    
    # Priority 3: Recently active users (48 hours)
    recently_active_48h = User.objects.filter(
        Q(last_login__gte=recent_48h) |
        Q(question__date__gte=recent_48h) |
        Q(answer__date__gte=recent_48h)
    ).exclude(id=user.id).exclude(id__in=chatted_user_ids).exclude(is_superuser=True).distinct()
    
    # Priority 4: Other active users
    other_active_users = User.objects.filter(
        is_active=True
    ).exclude(id=user.id).exclude(id__in=chatted_user_ids).exclude(is_superuser=True).order_by('-last_login')
    
    # Build prioritized list
    suggested_user_ids = []
    
    # Add mutual interaction users first (with recent activity preference)
    for u in mutual_interaction_users.filter(last_login__gte=recent_24h)[:3]:
        if u.id not in suggested_user_ids:
            suggested_user_ids.append(u.id)
    
    # Add more mutual interaction users
    for u in mutual_interaction_users[:5]:
        if u.id not in suggested_user_ids and len(suggested_user_ids) < limit:
            suggested_user_ids.append(u.id)
    
    # Add recently active users (24h)
    for u in recently_active_24h[:limit]:
        if u.id not in suggested_user_ids and len(suggested_user_ids) < limit:
            suggested_user_ids.append(u.id)
    
    # Add recently active users (48h)
    for u in recently_active_48h[:limit]:
        if u.id not in suggested_user_ids and len(suggested_user_ids) < limit:
            suggested_user_ids.append(u.id)
    
    # Fill remaining slots with other active users
    for u in other_active_users[:limit * 2]:
        if u.id not in suggested_user_ids and len(suggested_user_ids) < limit:
            suggested_user_ids.append(u.id)
    
    # Get user objects with profiles
    suggested_users = User.objects.filter(
        id__in=suggested_user_ids
    ).select_related('profile')
    
    # Build result with additional metadata
    result = []
    for u in suggested_users:
        # Determine activity status
        is_very_active = u.last_login and u.last_login >= recent_24h
        has_mutual_interaction = u.id in [mu.id for mu in mutual_interaction_users]
        
        result.append({
            'id': u.id,
            'username': u.username,
            'full_name': u.profile.full_name if hasattr(u, 'profile') and u.profile.full_name else u.get_full_name(),
            'photo': u.profile.profile_photo.url if hasattr(u, 'profile') and u.profile.profile_photo else None,
            'user_type': u.profile.user_type if hasattr(u, 'profile') else 'Student',
            'is_very_active': is_very_active,
            'has_mutual_interaction': has_mutual_interaction,
            'last_seen': u.last_login,
        })
    
    return result


@login_required
def chat_list(request):
    """Display list of all chats (private and group)"""
    user = request.user
    
    # Get all private chats for the user
    private_chats = PrivateChat.objects.filter(participants=user).prefetch_related('participants')
    
    # Get all group chats for the user
    group_chats = GroupChat.objects.filter(members=user)
    
    # Combine and sort by most recent activity
    all_chats = []
    
    for chat in private_chats:
        other_user = chat.get_other_user(user)
        if not other_user:
            continue  # Skip chats with no other participant
        
        latest_msg = chat.get_latest_message()
        
        # Get user's full name safely
        if hasattr(other_user, 'profile') and other_user.profile and other_user.profile.full_name:
            display_name = other_user.profile.full_name
        else:
            display_name = other_user.get_full_name() or other_user.username
        
        # Get profile photo safely
        photo_url = None
        if hasattr(other_user, 'profile') and other_user.profile and other_user.profile.profile_photo:
            photo_url = other_user.profile.profile_photo.url
        
        all_chats.append({
            'type': 'private',
            'id': chat.id,
            'user_id': other_user.id,  # Add other user's ID for URL
            'name': display_name,
            'photo': photo_url,
            'latest_message': latest_msg.content if latest_msg else 'No messages yet',
            'latest_message_time': latest_msg.created_at if latest_msg else None,
            'unread_count': ChatNotification.objects.filter(user=user, message__private_chat=chat, is_read=False).count(),
        })
    
    for chat in group_chats:
        latest_msg = chat.get_latest_message()
        all_chats.append({
            'type': 'group',
            'id': chat.id,
            'name': chat.name,
            'photo': chat.profile_photo.url if chat.profile_photo else None,
            'latest_message': latest_msg.content if latest_msg else 'No messages yet',
            'latest_message_time': latest_msg.created_at if latest_msg else None,
            'unread_count': ChatNotification.objects.filter(user=user, message__group_chat=chat, is_read=False).count(),
        })
    
    # Sort by latest message time
    all_chats.sort(key=lambda x: x['latest_message_time'] or timezone.now(), reverse=True)
    
    # Get suggested users for messaging (show 5-10 based on availability)
    suggested_users = get_suggested_users(user, limit=10)
    
    context = {
        'chats': all_chats,
        'private_chats_count': private_chats.count(),
        'group_chats_count': group_chats.count(),
        'suggested_users': suggested_users,
    }
    
    return render(request, 'chat/chat_list.html', context)


@login_required
def private_chat(request, user_id):
    """Display private chat with a specific user"""
    user = request.user
    
    # Check if other user exists
    try:
        other_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, f"User with ID {user_id} does not exist or has been deleted.")
        return redirect('chat:chat_list')
    
    if user == other_user:
        messages.error(request, "You cannot chat with yourself.")
        return redirect('chat:chat_list')
    
    # Get or create private chat
    chat = PrivateChat.objects.filter(participants=user).filter(participants=other_user).first()
    
    if not chat:
        chat = PrivateChat.objects.create()
        chat.participants.add(user, other_user)
    
    # Get chat messages
    chat_messages = chat.messages.all()
    
    # Mark notifications as read
    ChatNotification.objects.filter(user=user, message__private_chat=chat).update(is_read=True)
    
    # Paginate messages
    paginator = Paginator(chat_messages, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get recent chats for sidebar
    private_chats = PrivateChat.objects.filter(participants=user).prefetch_related('participants')[:10]
    recent_chats = []
    
    for pc in private_chats:
        other = pc.get_other_user(user)
        if not other:
            continue
        
        display_name = other.get_full_name() or other.username
        photo_url = None
        if hasattr(other, 'profile') and other.profile and other.profile.profile_photo:
            photo_url = other.profile.profile_photo.url
        
        recent_chats.append({
            'user_id': other.id,
            'name': display_name,
            'username': other.username,
            'photo': photo_url,
            'is_current': other.id == other_user.id,
        })
    
    context = {
        'chat': chat,
        'other_user': other_user,
        'messages': page_obj,
        'chat_type': 'private',
        'recent_chats': recent_chats,
    }
    
    return render(request, 'chat/private_chat.html', context)


@login_required
def group_chat(request, group_id):
    """Display group chat"""
    user = request.user
    
    # Check if group exists
    try:
        group = GroupChat.objects.get(id=group_id)
    except GroupChat.DoesNotExist:
        messages.error(request, f"Group chat with ID {group_id} does not exist or has been deleted.")
        return redirect('chat:chat_list')
    
    if user not in group.members.all():
        messages.error(request, "You are not a member of this group.")
        return redirect('chat:chat_list')
    
    # Get chat messages
    chat_messages = group.messages.all()
    
    # Mark notifications as read
    ChatNotification.objects.filter(user=user, message__group_chat=group).update(is_read=True)
    
    # Paginate messages
    paginator = Paginator(chat_messages, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get recent chats for sidebar
    private_chats = PrivateChat.objects.filter(participants=user).prefetch_related('participants')[:10]
    recent_chats = []
    
    for pc in private_chats:
        other = pc.get_other_user(user)
        if not other:
            continue
        
        display_name = other.get_full_name() or other.username
        photo_url = None
        if hasattr(other, 'profile') and other.profile and other.profile.profile_photo:
            photo_url = other.profile.profile_photo.url
        
        recent_chats.append({
            'user_id': other.id,
            'name': display_name,
            'username': other.username,
            'photo': photo_url,
            'is_current': False,
        })
    
    context = {
        'group': group,
        'messages': page_obj,
        'chat_type': 'group',
        'members': group.members.all(),
        'recent_chats': recent_chats,
    }
    
    return render(request, 'chat/group_chat.html', context)


@login_required
@require_http_methods(["POST"])
def send_message(request):
    """Send a message to a private or group chat"""
    try:
        data = json.loads(request.body)
        chat_type = data.get('chat_type')
        content = data.get('content', '').strip()
        
        if chat_type == 'private':
            chat_id = data.get('chat_id')
            chat = get_object_or_404(PrivateChat, id=chat_id)
            
            if request.user not in chat.participants.all():
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            message = Message.objects.create(
                sender=request.user,
                private_chat=chat,
                message_type='text',
                content=content
            )
        
        elif chat_type == 'group':
            chat_id = data.get('chat_id')
            chat = get_object_or_404(GroupChat, id=chat_id)
            
            if request.user not in chat.members.all():
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            message = Message.objects.create(
                sender=request.user,
                group_chat=chat,
                message_type='text',
                content=content
            )
        
        else:
            return JsonResponse({'error': 'Invalid chat type'}, status=400)
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'sender': message.sender.username,
            'content': message.content,
            'created_at': message.created_at.isoformat(),
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def send_image(request):
    """Send an image message"""
    try:
        chat_type = request.POST.get('chat_type')
        image = request.FILES.get('image')
        
        if not image:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        if chat_type == 'private':
            chat_id = request.POST.get('chat_id')
            chat = get_object_or_404(PrivateChat, id=chat_id)
            
            if request.user not in chat.participants.all():
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            message = Message.objects.create(
                sender=request.user,
                private_chat=chat,
                message_type='image',
                image=image,
                content='Sent an image'
            )
        
        elif chat_type == 'group':
            chat_id = request.POST.get('chat_id')
            chat = get_object_or_404(GroupChat, id=chat_id)
            
            if request.user not in chat.members.all():
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            message = Message.objects.create(
                sender=request.user,
                group_chat=chat,
                message_type='image',
                image=image,
                content='Sent an image'
            )
        
        else:
            return JsonResponse({'error': 'Invalid chat type'}, status=400)
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'image_url': message.image.url,
            'sender': message.sender.username,
            'created_at': message.created_at.isoformat(),
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def send_file(request):
    """Send a file message"""
    try:
        chat_type = request.POST.get('chat_type')
        file = request.FILES.get('file')
        
        if not file:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        if chat_type == 'private':
            chat_id = request.POST.get('chat_id')
            chat = get_object_or_404(PrivateChat, id=chat_id)
            
            if request.user not in chat.participants.all():
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            message = Message.objects.create(
                sender=request.user,
                private_chat=chat,
                message_type='file',
                file=file,
                content=f'Sent a file: {file.name}'
            )
        
        elif chat_type == 'group':
            chat_id = request.POST.get('chat_id')
            chat = get_object_or_404(GroupChat, id=chat_id)
            
            if request.user not in chat.members.all():
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            message = Message.objects.create(
                sender=request.user,
                group_chat=chat,
                message_type='file',
                file=file,
                content=f'Sent a file: {file.name}'
            )
        
        else:
            return JsonResponse({'error': 'Invalid chat type'}, status=400)
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'file_url': message.file.url,
            'file_name': file.name,
            'sender': message.sender.username,
            'created_at': message.created_at.isoformat(),
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def send_link(request):
    """Send a link message with metadata"""
    try:
        data = json.loads(request.body)
        chat_type = data.get('chat_type')
        link_url = data.get('link_url', '').strip()
        
        if not link_url:
            return JsonResponse({'error': 'No URL provided'}, status=400)
        
        # Fetch link metadata
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(link_url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            link_title = soup.find('meta', property='og:title')
            link_title = link_title['content'] if link_title else soup.title.string if soup.title else link_url
            
            link_description = soup.find('meta', property='og:description')
            link_description = link_description['content'] if link_description else ''
            
            link_image = soup.find('meta', property='og:image')
            link_image = link_image['content'] if link_image else None
        
        except:
            link_title = link_url
            link_description = ''
            link_image = None
        
        if chat_type == 'private':
            chat_id = data.get('chat_id')
            chat = get_object_or_404(PrivateChat, id=chat_id)
            
            if request.user not in chat.participants.all():
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            message = Message.objects.create(
                sender=request.user,
                private_chat=chat,
                message_type='link',
                link_url=link_url,
                link_title=link_title,
                link_description=link_description,
                link_image=link_image,
                content=link_url
            )
        
        elif chat_type == 'group':
            chat_id = data.get('chat_id')
            chat = get_object_or_404(GroupChat, id=chat_id)
            
            if request.user not in chat.members.all():
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            message = Message.objects.create(
                sender=request.user,
                group_chat=chat,
                message_type='link',
                link_url=link_url,
                link_title=link_title,
                link_description=link_description,
                link_image=link_image,
                content=link_url
            )
        
        else:
            return JsonResponse({'error': 'Invalid chat type'}, status=400)
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'link_url': message.link_url,
            'link_title': message.link_title,
            'link_description': message.link_description,
            'link_image': message.link_image,
            'sender': message.sender.username,
            'created_at': message.created_at.isoformat(),
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def create_group_chat(request):
    """Create a new group chat"""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        member_ids = data.get('member_ids', [])
        
        if not name:
            return JsonResponse({'error': 'Group name is required'}, status=400)
        
        if not member_ids:
            return JsonResponse({'error': 'At least one member is required'}, status=400)
        
        # Create group
        group = GroupChat.objects.create(
            name=name,
            creator=request.user
        )
        
        # Add creator and members
        group.members.add(request.user)
        
        for member_id in member_ids:
            try:
                member = User.objects.get(id=member_id)
                group.members.add(member)
            except User.DoesNotExist:
                pass
        
        return JsonResponse({
            'success': True,
            'group_id': group.id,
            'name': group.name,
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def add_group_member(request, group_id):
    """Add a member to a group chat"""
    try:
        group = get_object_or_404(GroupChat, id=group_id)
        
        if request.user != group.creator and request.user not in group.members.all():
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        user = get_object_or_404(User, id=user_id)
        group.members.add(user)
        
        return JsonResponse({
            'success': True,
            'message': f'{user.username} added to group'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def remove_group_member(request, group_id):
    """Remove a member from a group chat"""
    try:
        group = get_object_or_404(GroupChat, id=group_id)
        
        if request.user != group.creator:
            return JsonResponse({'error': 'Only group creator can remove members'}, status=403)
        
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        user = get_object_or_404(User, id=user_id)
        
        if user == group.creator:
            return JsonResponse({'error': 'Cannot remove group creator'}, status=400)
        
        group.members.remove(user)
        
        return JsonResponse({
            'success': True,
            'message': f'{user.username} removed from group'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def update_group_info(request, group_id):
    """Update group name and photo"""
    try:
        group = get_object_or_404(GroupChat, id=group_id)
        
        if request.user != group.creator:
            return JsonResponse({'error': 'Only group creator can update group info'}, status=403)
        
        name = request.POST.get('name', '').strip()
        photo = request.FILES.get('photo')
        
        if name:
            group.name = name
        
        if photo:
            group.profile_photo = photo
        
        group.save()
        
        return JsonResponse({
            'success': True,
            'name': group.name,
            'photo_url': group.profile_photo.url if group.profile_photo else None,
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def react_to_message(request, message_id):
    """Add emoji reaction to a message"""
    try:
        message = get_object_or_404(Message, id=message_id)
        data = json.loads(request.body)
        reaction = data.get('reaction')
        
        # Check if user has access to this message
        if message.private_chat and request.user not in message.private_chat.participants.all():
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        if message.group_chat and request.user not in message.group_chat.members.all():
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Create or delete reaction
        reaction_obj, created = MessageReaction.objects.get_or_create(
            message=message,
            user=request.user,
            reaction=reaction
        )
        
        if not created:
            reaction_obj.delete()
            return JsonResponse({'success': True, 'action': 'removed'})
        
        return JsonResponse({'success': True, 'action': 'added'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def get_unread_count(request):
    """Get count of unread messages"""
    try:
        unread_count = ChatNotification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({'unread_count': unread_count})
    except Exception as e:
        # Return 0 if there's a database lock or other error
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting unread count for user {request.user.id}: {str(e)}")
        return JsonResponse({'unread_count': 0}, status=200)
