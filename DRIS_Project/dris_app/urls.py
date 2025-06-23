# Your Name: Amir Ali Malekani Nezhad
# Student ID: S2009460

from django.urls import path  # type: ignore

from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # New Auth Paths
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('accounts/login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Citizen Management
    path('submit_disaster/', views.submit_disaster, name='submit_disaster'),
    path('disaster_reports/', views.disaster_reports, name='disaster_reports'),
    path('aid_request/', views.aid_request, name='aid_request'),
    path('my_requests/', views.my_requests, name='my_requests'),
    path('leave_shelter/', views.leave_shelter, name='leave_shelter'),

    # Volunteer Management
    path('volunteer_info/', views.volunteer_info, name='volunteer_info'),
    path('my_tasks/', views.my_tasks, name='my_tasks'),

    # Volunteer Assignment (Admin Only)
    path('assign_volunteer/', views.assign_volunteer, name='assign_volunteer'),

    # Shelter Management
    path('shelters/', views.shelters, name='shelters'),
    path('shelters/edit/<int:shelter_id>/', views.edit_shelter, name='edit_shelter'),
    path('shelters/delete/<int:shelter_id>/', views.delete_shelter, name='delete_shelter'),
    path('assign_shelter/', views.assign_shelter, name='assign_shelter'),
]