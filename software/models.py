from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class BaseModel(models.Model):
    """
    Abstract base model that provides common fields for all models
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True

class SoftwareCategory(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Software(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    version = models.CharField(max_length=50, default="1.0")
    category = models.ForeignKey(SoftwareCategory, on_delete=models.SET_NULL, null=True)
    upload_date = models.DateTimeField(default=timezone.now)
    update_date = models.DateTimeField(auto_now=True)
    uploader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='software_files/')
    thumbnail = models.ImageField(upload_to='software_thumbnails/', blank=True, null=True)
    download_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} (v{self.version})"

    def increment_download_count(self):
        self.download_count += 1
        self.save()