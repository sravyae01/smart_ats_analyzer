# analyzer/models.py
from django.db import models
from django.conf import settings
import uuid

class Analysis(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analyses')
    
    # Files and input
    resume_file = models.FileField(upload_to='resumes/%Y/%m/%d/')
    job_description = models.TextField()
    job_title = models.CharField(max_length=255, blank=True)
    
    # Extracted text
    resume_text = models.TextField(blank=True)
    
    # Scores (0-100)
    ats_score = models.IntegerField(default=0)
    critical_skills_match = models.FloatField(default=0)
    skills_match = models.FloatField(default=0)
    profile_match = models.FloatField(default=0)
    format_score = models.FloatField(default=0)
    
    # Keyword tracking
    missing_keywords = models.JSONField(default=list)  # ['Kubernetes', 'AWS']
    found_keywords = models.JSONField(default=list)
    critical_skills = models.JSONField(default=list)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processing_time = models.FloatField(null=True, blank=True)  # in seconds
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.ats_score}% - {self.created_at.date()}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Analyses'

class ResumeVersion(models.Model):
    """Track different versions of user's resume"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, null=True, blank=True)
    version_number = models.IntegerField()
    content = models.TextField()  # Full resume text
    file = models.FileField(upload_to='versions/%Y/%m/%d/')
    ats_score = models.IntegerField()
    parent_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'version_number']
        ordering = ['-version_number']

class HeatmapData(models.Model):
    """Store heatmap coordinates for visual feedback"""
    analysis = models.OneToOneField(Analysis, on_delete=models.CASCADE, related_name='heatmap')
    priority_zones = models.JSONField(default=dict)  # Coordinates for recruiter eye-tracking
    keyword_positions = models.JSONField(default=dict)  # Where each keyword appears
    heatmap_image = models.ImageField(upload_to='heatmaps/%Y/%m/%d/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class RewriteSuggestion(models.Model):
    """Store AI-generated rewrite suggestions"""
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name='rewrites')
    original_text = models.TextField()
    suggested_text = models.TextField()
    context_section = models.CharField(max_length=100)  # summary, skills, experience, education
    keyword_added = models.CharField(max_length=255, blank=True)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)