from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    path('client/', views.ClientDashboardView.as_view(), name='client_dashboard'),
    path('client/applications/', views.ClientApplicationListView.as_view(), name='client_applications'),
    path('client/application/create/', views.ClientApplicationCreateView.as_view(), name='client_application_create'),

    path('referrer/', views.ReferrerDashboardView.as_view(), name='referrer_dashboard'),
    path('referrer/applications/', views.ReferrerApplicationListView.as_view(), name='referrer_applications'),
    path('referrer/application/<int:pk>/', views.ReferrerApplicationDetailView.as_view(), name='referrer_application_detail'),
    path('referrer/report/create/', views.ReferrerReportCreateView.as_view(), name='referrer_report_create'),

    path('admin-panel/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-panel/users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('admin-panel/user/<int:pk>/', views.AdminUserUpdateView.as_view(), name='admin_user_edit'),

    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('document/upload/<int:application_id>/', views.DocumentUploadView.as_view(), name='document_upload'),
    path('notifications/<int:pk>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('document/download/<int:doc_id>/', views.download_document, name='download_document'),
] 