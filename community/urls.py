from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    # Community listing and discovery
    path('', views.community_list, name='community_list'),
    path('my-communities/', views.my_communities, name='my_communities'),
    
    # Community CRUD
    path('create/', views.create_community, name='create_community'),
    path('<slug:slug>/', views.community_detail, name='community_detail'),
    path('<slug:slug>/members/', views.community_members, name='community_members'),
    
    # Community membership
    path('<slug:slug>/join/', views.join_community, name='join_community'),
    path('<slug:slug>/leave/', views.leave_community, name='leave_community'),
]
