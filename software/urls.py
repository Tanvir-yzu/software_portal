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
    
        # Static pages - Class-based views
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms-of-service/', views.TermsOfServiceView.as_view(), name='terms_of_service'),
    path('contact-us/', views.ContactUsView.as_view(), name='contact_us'),
    path('about-us/', views.AboutUsView.as_view(), name='about_us'),
]