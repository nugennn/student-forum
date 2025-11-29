from django.contrib import admin
from .models import CampusUpdate


@admin.register(CampusUpdate)
class CampusUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'priority', 'category', 'is_published', 'created_at')
    list_filter = ('priority', 'category', 'is_published', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Notice Information', {
            'fields': ('title', 'content', 'category', 'priority')
        }),
        ('Media', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'expiry_date')
        }),
        ('Metadata', {
            'fields': ('author', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)
