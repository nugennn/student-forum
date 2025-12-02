from django.urls import path,include

from . import views

app_name = 'users'

urlpatterns = [
	# path('',include('django.contrib.auth.urls')),
	
	path('signup_view/',views.signup_view, name='signup_view'),
	
	path('logout_view/', views.logout_view, name='logout_view'),
	
	path("login_request", views.login_request, name="login_request"),
	
	path('force_password_change/', views.force_password_change, name='force_password_change'),
	
	# Password Reset URLs
	path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
	path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
	path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
	path('password-reset-complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
	
	# path('login/', views.LoginView.as_view(), name='logins'),
]

