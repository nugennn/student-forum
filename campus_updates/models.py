from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CampusUpdate(models.Model):
    """Model for college notices and campus updates posted by teachers/admins"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200, help_text="Title of the notice")
    content = models.TextField(help_text="Detailed content of the notice")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campus_updates')
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level of the notice"
    )
    
    category = models.CharField(
        max_length=50,
        choices=[
            ('academic', 'Academic'),
            ('event', 'Event'),
            ('maintenance', 'Maintenance'),
            ('holiday', 'Holiday'),
            ('announcement', 'Announcement'),
            ('other', 'Other'),
        ],
        default='announcement'
    )
    
    image = models.ImageField(
        upload_to='campus_updates/',
        null=True,
        blank=True,
        help_text="Optional image for the notice"
    )
    
    is_published = models.BooleanField(
        default=True,
        help_text="Whether the notice is visible to students"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional fields
    expiry_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when the notice expires"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Campus Update'
        verbose_name_plural = 'Campus Updates'
    
    def __str__(self):
        return self.title
    
    def is_expired(self):
        """Check if the notice has expired"""
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False
    
    def get_priority_color(self):
        """Return color code for priority level"""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'urgent': '#dc3545',
        }
        return colors.get(self.priority, '#6c757d')
