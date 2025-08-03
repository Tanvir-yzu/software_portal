from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from django.utils import timezone
from software.models import Software, SoftwareCategory


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return [
            'software:software_list',
            'software:privacy_policy',
            'software:terms_of_service',
            'software:contact_us',
            'software:about_us',
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        # Return current time for static pages
        return timezone.now()


class SoftwareSitemap(Sitemap):
    """Sitemap for individual software pages"""
    changefreq = 'weekly'
    priority = 0.9
    protocol = 'https'

    def items(self):
        return Software.objects.filter(is_active=True).select_related('category')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('software:software_detail', args=[obj.pk])

    def priority(self, obj):
        # Higher priority for software with more downloads
        if obj.download_count > 1000:
            return 1.0
        elif obj.download_count > 500:
            return 0.9
        elif obj.download_count > 100:
            return 0.8
        else:
            return 0.7


class CategorySitemap(Sitemap):
    """Sitemap for category-filtered software list pages"""
    changefreq = 'daily'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return SoftwareCategory.objects.filter(
            is_active=True,
            software__is_active=True
        ).distinct()

    def lastmod(self, obj):
        # Get the latest update from software in this category
        latest_software = Software.objects.filter(
            category=obj,
            is_active=True
        ).order_by('-updated_at').first()
        
        if latest_software:
            return latest_software.updated_at
        return obj.updated_at

    def location(self, obj):
        return f"{reverse('software:software_list')}?category={obj.pk}"


class SoftwareAPISitemap(Sitemap):
    """Sitemap for API endpoints (if they should be indexed)"""
    changefreq = 'daily'
    priority = 0.3
    protocol = 'https'

    def items(self):
        return [
            'software:software_api',
            'software:category_api',
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        return timezone.now()


# Sitemap registry
sitemaps = {
    'static': StaticViewSitemap,
    'software': SoftwareSitemap,
    'categories': CategorySitemap,
    'api': SoftwareAPISitemap,
}