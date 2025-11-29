from django.urls import path
from . import views

app_name = 'campus_updates'

urlpatterns = [
    # Student/Public views
    path('', views.campus_updates_list, name='updates_list'),
    path('update/<int:pk>/', views.update_detail, name='update_detail'),
    
    # Teacher/Admin views
    path('create/', views.create_update, name='create_update'),
    path('manage/', views.manage_updates, name='manage_updates'),
    path('edit/<int:pk>/', views.edit_update, name='edit_update'),
    path('delete/<int:pk>/', views.delete_update, name='delete_update'),
]
