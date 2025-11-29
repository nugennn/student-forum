from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import CampusUpdate
from .forms import CampusUpdateForm


def is_teacher_or_admin(user):
    """Check if user is a teacher or admin"""
    return user.is_staff or user.is_superuser or user.profile.is_teacher


@login_required
def campus_updates_list(request):
    """Display all campus updates for students and teachers"""
    updates = CampusUpdate.objects.filter(is_published=True)
    
    # Filter out expired notices
    updates = [u for u in updates if not u.is_expired()]
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        updates = [u for u in updates if search_query.lower() in u.title.lower() or search_query.lower() in u.content.lower()]
    
    # Category filter
    category = request.GET.get('category', '')
    if category:
        updates = [u for u in updates if u.category == category]
    
    # Priority filter
    priority = request.GET.get('priority', '')
    if priority:
        updates = [u for u in updates if u.priority == priority]
    
    # Pagination
    paginator = Paginator(updates, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'updates': page_obj.object_list,
        'search_query': search_query,
        'selected_category': category,
        'selected_priority': priority,
    }
    return render(request, 'campus_updates/updates_list.html', context)


@login_required
@user_passes_test(is_teacher_or_admin)
def create_update(request):
    """Create a new campus update (teachers/admins only)"""
    if request.method == 'POST':
        form = CampusUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            update = form.save(commit=False)
            update.author = request.user
            update.save()
            messages.success(request, 'Campus update posted successfully!')
            return redirect('campus_updates:updates_list')
    else:
        form = CampusUpdateForm()
    
    context = {'form': form}
    return render(request, 'campus_updates/create_update.html', context)


@login_required
@user_passes_test(is_teacher_or_admin)
def edit_update(request, pk):
    """Edit an existing campus update (author or admin only)"""
    update = get_object_or_404(CampusUpdate, pk=pk)
    
    # Check if user is author or admin
    if update.author != request.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit this update.')
        return redirect('campus_updates:updates_list')
    
    if request.method == 'POST':
        form = CampusUpdateForm(request.POST, request.FILES, instance=update)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campus update updated successfully!')
            return redirect('campus_updates:update_detail', pk=update.pk)
    else:
        form = CampusUpdateForm(instance=update)
    
    context = {'form': form, 'update': update}
    return render(request, 'campus_updates/edit_update.html', context)


@login_required
def update_detail(request, pk):
    """View detailed campus update"""
    update = get_object_or_404(CampusUpdate, pk=pk)
    
    # Check if update is published or user is author/admin
    if not update.is_published and update.author != request.user and not request.user.is_superuser:
        messages.error(request, 'This update is not available.')
        return redirect('campus_updates:updates_list')
    
    context = {'update': update}
    return render(request, 'campus_updates/update_detail.html', context)


@login_required
@user_passes_test(is_teacher_or_admin)
def delete_update(request, pk):
    """Delete a campus update (author or admin only)"""
    update = get_object_or_404(CampusUpdate, pk=pk)
    
    # Check if user is author or admin
    if update.author != request.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete this update.')
        return redirect('campus_updates:updates_list')
    
    if request.method == 'POST':
        update.delete()
        messages.success(request, 'Campus update deleted successfully!')
        return redirect('campus_updates:updates_list')
    
    context = {'update': update}
    return render(request, 'campus_updates/delete_update.html', context)


@login_required
@user_passes_test(is_teacher_or_admin)
def manage_updates(request):
    """Manage all campus updates (teachers/admins view)"""
    updates = CampusUpdate.objects.all()
    
    # Filter by author if not superuser
    if not request.user.is_superuser:
        updates = updates.filter(author=request.user)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        updates = updates.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
    
    # Pagination
    paginator = Paginator(updates, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'updates': page_obj.object_list,
        'search_query': search_query,
    }
    return render(request, 'campus_updates/manage_updates.html', context)
