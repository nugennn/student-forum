from django.contrib import admin
from .models import PrivateChat, GroupChat, Message, MessageReaction, ChatNotification


@admin.register(PrivateChat)
class PrivateChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('participants__username',)
    
    def get_participants(self, obj):
        return ', '.join([u.username for u in obj.participants.all()])
    get_participants.short_description = 'Participants'


@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'get_member_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'creator__username', 'members__username')
    filter_horizontal = ('members',)
    
    def get_member_count(self, obj):
        return obj.members.count()
    get_member_count.short_description = 'Members'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'message_type', 'get_chat_type', 'created_at', 'is_edited')
    list_filter = ('message_type', 'created_at', 'is_edited')
    search_fields = ('sender__username', 'content')
    readonly_fields = ('created_at', 'edited_at')
    
    def get_chat_type(self, obj):
        if obj.private_chat:
            return 'Private'
        elif obj.group_chat:
            return 'Group'
        return 'Unknown'
    get_chat_type.short_description = 'Chat Type'


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'reaction', 'get_message_sender', 'created_at')
    list_filter = ('reaction', 'created_at')
    search_fields = ('user__username', 'message__sender__username')
    
    def get_message_sender(self, obj):
        return obj.message.sender.username
    get_message_sender.short_description = 'Message Sender'


@admin.register(ChatNotification)
class ChatNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_message_sender', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message__sender__username')
    
    def get_message_sender(self, obj):
        return obj.message.sender.username
    get_message_sender.short_description = 'Message Sender'
