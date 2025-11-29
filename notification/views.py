from django.shortcuts import render
from .models import PrivRepNotification,Notification
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(["POST"])
def read_All_Notifications(request):

    notifics = Notification.objects.filter(noti_receiver=request.user).order_by('-date_created')

    for objs in notifics:
        objs.is_read = True
        objs.save()

    # return HttpResponse(status=204)
    return JsonResponse({'action': 'readedAll', 'success': True})

@login_required
@require_http_methods(["POST"])
def delete_notification(request, notification_id):
    """Delete a single notification"""
    try:
        notification = Notification.objects.get(id=notification_id, noti_receiver=request.user)
        notification.delete()
        return JsonResponse({'success': True, 'message': 'Notification deleted'})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Notification not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def delete_all_notifications(request):
    """Delete all notifications for the user"""
    try:
        deleted_count, _ = Notification.objects.filter(noti_receiver=request.user).delete()
        return JsonResponse({'success': True, 'message': f'Deleted {deleted_count} notifications'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

def read_All_Priv_Notifications(request):

    notifications = PrivRepNotification.objects.filter(for_user=request.user)

    for obj in notifications:
        obj.is_read = True
        obj.save()

    return JsonResponse({'action':'readedAllPrivNotifications'})

