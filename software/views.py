from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, Http404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Software, SoftwareCategory

class SoftwareListView(ListView):
    model = Software
    template_name = 'software/software_list.html'
    context_object_name = 'software_list'
    paginate_by = 12
    ordering = ['-upload_date']
    
    def get_queryset(self):
        queryset = Software.objects.filter(is_active=True).select_related('category', 'uploader')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(version__icontains=search_query)
            )
        
        # Category filter
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = SoftwareCategory.objects.filter(is_active=True)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context

class SoftwareDetailView(DetailView):
    model = Software
    template_name = 'software/software_detail.html'
    context_object_name = 'software'
    
    def get_queryset(self):
        return Software.objects.filter(is_active=True).select_related('category', 'uploader')

def software_download(request, pk):
    """Handle software download and increment download count"""
    import os
    software = get_object_or_404(Software, pk=pk, is_active=True)
    
    # Increment download count
    software.increment_download_count()
    
    # Return file download response
    if software.file:
        # Get the original filename from the file path
        original_filename = os.path.basename(software.file.name)
        
        response = HttpResponse(software.file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{original_filename}"'
        return response
    else:
        raise Http404("File not found")

class SoftwareAPIView(View):
    """API endpoint for software data"""
    
    def get(self, request):
        software_list = Software.objects.filter(is_active=True).select_related('category', 'uploader')
        
        # Apply filters
        search = request.GET.get('search')
        if search:
            software_list = software_list.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        category_id = request.GET.get('category')
        if category_id:
            software_list = software_list.filter(category_id=category_id)
        
        # Serialize data
        data = []
        for software in software_list[:20]:  # Limit to 20 items
            data.append({
                'id': software.id,
                'title': software.title,
                'description': software.description,
                'version': software.version,
                'category': software.category.name if software.category else None,
                'download_count': software.download_count,
                'upload_date': software.upload_date.isoformat(),
                'thumbnail': software.thumbnail.url if software.thumbnail else None,
            })
        
        return JsonResponse({'software': data})

class CategoryAPIView(View):
    """API endpoint for categories"""
    
    def get(self, request):
        categories = SoftwareCategory.objects.filter(is_active=True)
        data = []
        for category in categories:
            data.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'software_count': category.software_set.filter(is_active=True).count()
            })
        
        return JsonResponse({'categories': data})