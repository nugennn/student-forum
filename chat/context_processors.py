from chat.models import ChatNotification


def count_unread_chat_messages(request):
    """Context processor to count unread chat messages"""
    if request.user.is_authenticated:
        try:
            unread_count = ChatNotification.objects.filter(user=request.user, is_read=False).count()
            return {'countUnreadChats': unread_count}
        except Exception as e:
            return {'countUnreadChats': 0}
    else:
        return {'countUnreadChats': 0}
