from django.contrib import admin
from .models import SoftwareCategory, Software

@admin.register(SoftwareCategory)
class SoftwareCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    ordering = ('name',)

@admin.register(Software)
class SoftwareAdmin(admin.ModelAdmin):
    list_display = ('title', 'version', 'category', 'uploader', 'download_count', 'is_active', 'upload_date')
    list_filter = ('category', 'is_active', 'upload_date', 'uploader')
    search_fields = ('title', 'description', 'version')
    list_editable = ('is_active',)
    readonly_fields = ('download_count', 'created_at', 'updated_at', 'upload_date', 'update_date')
    ordering = ('-upload_date',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'version', 'category')
        }),
        ('Files', {
            'fields': ('file', 'thumbnail')
        }),
        ('Metadata', {
            'fields': ('uploader', 'download_count', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'upload_date', 'update_date'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('category', 'uploader')