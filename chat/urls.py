from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Chat list and views
    path('', views.chat_list, name='chat_list'),
    path('private/<int:user_id>/', views.private_chat, name='private_chat'),
    path('group/<int:group_id>/', views.group_chat, name='group_chat'),
    
    # Message operations
    path('send-message/', views.send_message, name='send_message'),
    path('send-image/', views.send_image, name='send_image'),
    path('send-file/', views.send_file, name='send_file'),
    path('send-link/', views.send_link, name='send_link'),
    
    # Group operations
    path('create-group-page/', views.create_group_page, name='create_group_page'),
    path('create-group/', views.create_group_chat, name='create_group'),
    path('group/<int:group_id>/add-member/', views.add_group_member, name='add_member'),
    path('group/<int:group_id>/remove-member/', views.remove_group_member, name='remove_member'),
    path('group/<int:group_id>/update-info/', views.update_group_info, name='update_group_info'),
    
    # Reactions
    path('message/<int:message_id>/react/', views.react_to_message, name='react_to_message'),
    
    # Notifications
    path('unread-count/', views.get_unread_count, name='unread_count'),
    
    # Users
    path('get-users/', views.get_users, name='get_users'),
]
