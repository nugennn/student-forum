from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    # Community listing and discovery
    path('', views.community_list, name='community_list'),
    path('my-communities/', views.my_communities, name='my_communities'),
    
    # Community CRUD
    path('create/', views.create_community, name='create_community'),
    path('<slug:slug>/delete/', views.delete_community, name='delete_community'),
    path('<slug:slug>/', views.community_detail, name='community_detail'),
    path('<slug:slug>/edit/', views.edit_community, name='edit_community'),
    path('<slug:slug>/members/', views.community_members, name='community_members'),
    
    # Community membership
    path('<slug:slug>/manage-members/', views.community_members, name='manage_members'),
    path('<slug:slug>/join/', views.join_community, name='join_community'),
    path('<slug:slug>/leave/', views.leave_community, name='leave_community'),
    path('<slug:slug>/members/remove/<int:user_id>/', views.remove_member, name='remove_member'),
    path('<slug:slug>/members/change-role/<int:user_id>/', views.change_member_role, name='change_member_role'),
]
