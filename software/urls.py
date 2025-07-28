from django.urls import path
from . import views

app_name = 'software'

urlpatterns = [
    # Software list view (homepage)
    path('', views.SoftwareListView.as_view(), name='software_list'),
    
    # Software detail view
    path('software/<int:pk>/', views.SoftwareDetailView.as_view(), name='software_detail'),
    
    # Software download
    path('software/<int:pk>/download/', views.software_download, name='software_download'),
    
    # API endpoints
    path('api/software/', views.SoftwareAPIView.as_view(), name='software_api'),
    path('api/categories/', views.CategoryAPIView.as_view(), name='category_api'),
]