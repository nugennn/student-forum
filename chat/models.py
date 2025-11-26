from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class PrivateChat(models.Model):
    """Model for private one-on-one chats between two users"""
    participants = models.ManyToManyField(User, related_name='private_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat: {', '.join([u.username for u in self.participants.all()])}"

    def get_other_user(self, user):
        """Get the other participant in the chat"""
        return self.participants.exclude(id=user.id).first()

    def get_latest_message(self):
        """Get the most recent message in this chat"""
        return self.messages.order_by('-created_at').first()


class GroupChat(models.Model):
    """Model for group chats with multiple participants"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='group_chat_photos', default='media/isle.jpg')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_group_chats')
    members = models.ManyToManyField(User, related_name='group_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    def get_latest_message(self):
        """Get the most recent message in this group chat"""
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    """Model for messages in both private and group chats"""
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('link', 'Link'),
    ]

    # Relationships
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    private_chat = models.ForeignKey(PrivateChat, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    group_chat = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)

    # Content
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField()  # Text content or file path
    
    # Media
    image = models.ImageField(upload_to='chat_images', null=True, blank=True)
    file = models.FileField(upload_to='chat_files', null=True, blank=True)
    
    # Link metadata
    link_url = models.URLField(null=True, blank=True)
    link_title = models.CharField(max_length=255, null=True, blank=True)
    link_description = models.TextField(null=True, blank=True)
    link_image = models.URLField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_edited = models.BooleanField(default=False)

    # Status
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        # Return just the content preview instead of sender info
        if self.content:
            return self.content[:50] + ('...' if len(self.content) > 50 else '')
        return f"{self.message_type.capitalize()} message"

    def mark_as_edited(self):
        """Mark message as edited"""
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save()


class MessageReaction(models.Model):
    """Model for reactions to messages (emoji reactions)"""
    REACTION_CHOICES = [
        ('👍', 'Thumbs Up'),
        ('❤️', 'Heart'),
        ('😂', 'Laughing'),
        ('😮', 'Surprised'),
        ('😢', 'Sad'),
        ('🔥', 'Fire'),
    ]

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user', 'reaction')

    def __str__(self):
        return f"{self.user.username} reacted {self.reaction} to message"


class ChatNotification(models.Model):
    """Model for tracking unread messages"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'message')

    def __str__(self):
        return f"Notification for {self.user.username}"


@receiver(post_save, sender=Message)
def create_chat_notifications(sender, instance, created, **kwargs):
    """Create notifications for all recipients when a message is sent"""
    if created:
        if instance.private_chat:
            # For private chats, notify the other participant
            recipients = instance.private_chat.participants.exclude(id=instance.sender.id)
        elif instance.group_chat:
            # For group chats, notify all members except sender
            recipients = instance.group_chat.members.exclude(id=instance.sender.id)
        else:
            recipients = []

        for recipient in recipients:
            ChatNotification.objects.create(user=recipient, message=instance)
