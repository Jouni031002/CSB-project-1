from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/<int:user_id>/', views.profile_detail),
    path('search/', views.search_users),
    path('xss/', views.xss_demo),
    path('fetch/', views.fetch_url),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='core/login.html')),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('debug-info/', views.debug_info),
]