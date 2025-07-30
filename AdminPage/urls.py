from django.urls import path
from . import views

app_name = 'adminpage'

urlpatterns = [
    path('', views.AdminHomeView.as_view(), name='admin_home'),
    path('stats/', views.AdminStatsView.as_view(), name='admin_stats'),
    path('upload/', views.AdminSoftwareUploadView.as_view(), name='software_upload'),
    path('software/', views.AdminSoftwareListView.as_view(), name='software_list'),
    path('software/edit/<int:pk>/', views.AdminSoftwareEditView.as_view(), name='software_edit'),
    path('software/delete/<int:pk>/', views.AdminSoftwareDeleteView.as_view(), name='software_delete'),
    path('software/toggle/<int:pk>/', views.AdminSoftwareToggleStatusView.as_view(), name='software_toggle'),
    path('software/details/<int:pk>/', views.get_software_details, name='software_details'),
]