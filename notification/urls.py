from django.urls import path
from . import views

app_name = 'notification'

urlpatterns = [

	path('read_All_Notifications/', views.read_All_Notifications, name='read_All_Notifications'),
	path('mark-all-read/', views.read_All_Notifications, name='mark_all_read'),
	path('delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
	path('delete-all/', views.delete_all_notifications, name='delete_all_notifications'),

	path('read_All_Priv_Notifications/', views.read_All_Priv_Notifications, name='read_All_Priv_Notifications'),


]