from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from software.models import Software, SoftwareCategory
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django import forms
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class SoftwareUploadForm(forms.ModelForm):
    """
    Form for uploading software through admin panel
    """
    class Meta:
        model = Software
        fields = ['title', 'description', 'version', 'category', 'file', 'thumbnail', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter software title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Enter software description'
            }),
            'version': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g., 1.0.0'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'file': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': '.exe,.msi,.zip,.rar,.dmg,.pkg,.deb,.rpm,.tar.gz'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = SoftwareCategory.objects.filter(is_active=True)
        self.fields['category'].empty_label = "Select a category"
        self.fields['is_active'].initial = True

class AdminHomeView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Class-based view for the admin home page dashboard
    """
    template_name = 'AdminPage/admin_home.html'
    login_url = '/admin/login/'
    
    def test_func(self):
        """Check if user is staff or superuser"""
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current date and calculate date ranges
        now = timezone.now()
        today = now.date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Dashboard statistics
        context.update({
            # Total counts
            'total_software': Software.objects.filter(is_active=True).count(),
            'total_categories': SoftwareCategory.objects.filter(is_active=True).count(),
            'total_users': User.objects.filter(is_active=True).count(),
            'total_downloads': Software.objects.aggregate(
                total=Sum('download_count')
            )['total'] or 0,
            
            # Recent statistics
            'software_this_week': Software.objects.filter(
                created_at__date__gte=week_ago,
                is_active=True
            ).count(),
            'software_this_month': Software.objects.filter(
                created_at__date__gte=month_ago,
                is_active=True
            ).count(),
            'new_users_this_week': User.objects.filter(
                date_joined__date__gte=week_ago,
                is_active=True
            ).count(),
            
            # Recent software uploads
            'recent_software': Software.objects.filter(
                is_active=True
            ).select_related('category', 'uploader').order_by('-created_at')[:10],
            
            # Popular software (by download count)
            'popular_software': Software.objects.filter(
                is_active=True
            ).select_related('category', 'uploader').order_by('-download_count')[:10],
            
            # Category statistics
            'category_stats': SoftwareCategory.objects.filter(
                is_active=True
            ).annotate(
                software_count=Count('software', filter=Q(software__is_active=True))
            ).order_by('-software_count')[:10],
            
            # Recent users
            'recent_users': User.objects.filter(
                is_active=True
            ).order_by('-date_joined')[:10],
            
            # Inactive software (for review)
            'inactive_software': Software.objects.filter(
                is_active=False
            ).select_related('category', 'uploader').order_by('-created_at')[:5],
            
            # System status
            'pending_reviews': Software.objects.filter(is_active=False).count(),
            'active_categories': SoftwareCategory.objects.filter(is_active=True).count(),
            'inactive_categories': SoftwareCategory.objects.filter(is_active=False).count(),
        })
        
        return context

class AdminStatsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Detailed statistics view for admin
    """
    template_name = 'AdminPage/admin_stats.html'
    login_url = '/admin/login/'
    
    def test_func(self):
        """Check if user is staff or superuser"""
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get detailed statistics
        now = timezone.now()
        
        # Monthly data for charts (last 12 months)
        monthly_data = []
        for i in range(12):
            month_start = (now - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            monthly_data.append({
                'month': month_start.strftime('%B %Y'),
                'software_count': Software.objects.filter(
                    created_at__date__range=[month_start.date(), month_end.date()],
                    is_active=True
                ).count(),
                'user_count': User.objects.filter(
                    date_joined__date__range=[month_start.date(), month_end.date()],
                    is_active=True
                ).count(),
            })
        
        context.update({
            'monthly_data': list(reversed(monthly_data)),
            'top_uploaders': User.objects.annotate(
                upload_count=Count('software', filter=Q(software__is_active=True)),
                total_downloads=Sum('software__download_count', filter=Q(software__is_active=True))
            ).filter(upload_count__gt=0).order_by('-upload_count')[:10],
            
            'download_stats': Software.objects.filter(
                is_active=True
            ).aggregate(
                total_downloads=Sum('download_count'),
                avg_downloads=Sum('download_count') / Count('id') if Software.objects.filter(is_active=True).count() > 0 else 0
            ),
        })
        
        return context

class AdminSoftwareUploadView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    View for uploading software through admin panel
    """
    model = Software
    form_class = SoftwareUploadForm
    template_name = 'AdminPage/software_upload.html'
    success_url = reverse_lazy('adminpage:software_list')
    login_url = '/admin/login/'
    
    def test_func(self):
        """Check if user is staff or superuser"""
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def form_valid(self, form):
        """Set the uploader to current user before saving"""
        form.instance.uploader = self.request.user
        messages.success(self.request, f'Software "{form.instance.title}" has been uploaded successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        messages.error(self.request, 'Please correct the errors below and try again.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Upload Software',
            'categories': SoftwareCategory.objects.filter(is_active=True),
            'recent_uploads': Software.objects.filter(
                uploader=self.request.user
            ).order_by('-created_at')[:5]
        })
        return context

class AdminSoftwareListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    View for managing uploaded software
    """
    template_name = 'AdminPage/software_list.html'
    login_url = '/admin/login/'
    
    def test_func(self):
        """Check if user is staff or superuser"""
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all software with filtering options
        software_list = Software.objects.select_related('category', 'uploader').order_by('-created_at')
        
        # Filter by status if requested
        status_filter = self.request.GET.get('status', 'all')
        if status_filter == 'active':
            software_list = software_list.filter(is_active=True)
        elif status_filter == 'inactive':
            software_list = software_list.filter(is_active=False)
        
        # Filter by category if requested
        category_filter = self.request.GET.get('category')
        if category_filter:
            software_list = software_list.filter(category_id=category_filter)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            software_list = software_list.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(uploader__username__icontains=search_query)
            )
        
        context.update({
            'software_list': software_list,
            'categories': SoftwareCategory.objects.filter(is_active=True),
            'status_filter': status_filter,
            'category_filter': category_filter,
            'search_query': search_query or '',
            'total_software': software_list.count(),
        })
        
        return context

class AdminSoftwareEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View for editing software through admin panel
    """
    model = Software
    form_class = SoftwareUploadForm
    template_name = 'AdminPage/software_edit.html'
    success_url = reverse_lazy('adminpage:software_list')
    login_url = '/admin/login/'
    
    def test_func(self):
        """Check if user is staff or superuser"""
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def form_valid(self, form):
        """Handle successful form submission"""
        messages.success(self.request, f'Software "{form.instance.title}" has been updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        messages.error(self.request, 'Please correct the errors below and try again.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Edit Software',
            'categories': SoftwareCategory.objects.filter(is_active=True),
            'is_edit': True,
        })
        return context

class AdminSoftwareDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View for deleting software through admin panel
    """
    model = Software
    success_url = reverse_lazy('adminpage:software_list')
    login_url = '/admin/login/'
    
    def test_func(self):
        """Check if user is staff or superuser"""
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def delete(self, request, *args, **kwargs):
        """Handle deletion with success message"""
        software = self.get_object()
        software_title = software.title
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Software "{software_title}" has been deleted successfully!')
        return response

@method_decorator(csrf_exempt, name='dispatch')
class AdminSoftwareToggleStatusView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    AJAX view for toggling software active status
    """
    login_url = '/admin/login/'
    
    def test_func(self):
        """Check if user is staff or superuser"""
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def post(self, request, pk):
        """Toggle software active status"""
        try:
            software = get_object_or_404(Software, pk=pk)
            software.is_active = not software.is_active
            software.save()
            
            return JsonResponse({
                'success': True,
                'is_active': software.is_active,
                'message': f'Software "{software.title}" has been {"activated" if software.is_active else "deactivated"}.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating software status: {str(e)}'
            })

def get_software_details(request, pk):
    """
    AJAX view to get software details for edit modal
    """
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        software = get_object_or_404(Software, pk=pk)
        data = {
            'id': software.id,
            'title': software.title,
            'description': software.description,
            'version': software.version,
            'category': software.category.id if software.category else '',
            'is_active': software.is_active,
            'thumbnail_url': software.thumbnail.url if software.thumbnail else '',
            'file_name': software.file.name.split('/')[-1] if software.file else '',
            'uploader': software.uploader.username,
            'created_at': software.created_at.strftime('%Y-%m-%d %H:%M'),
            'download_count': software.download_count,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)