# accounts/models.py - COMPLETE ERROR-FREE VERSION
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    ROLE_CHOICES = (
        ('job_seeker', '🔍 Job Seeker (Actively looking for jobs)'),
        ('fresher', '🎓 Fresher / Recent Graduate'),
        ('student', '📚 Student (UG/PG)'),
        ('experienced', '💼 Experienced Professional (3+ years)'),
        ('career_changer', '🔄 Career Changer'),
        ('internship', '📝 Looking for Internship'),
        ('recruiter', '👔 Recruiter / HR Professional'),
        ('freelancer', '💻 Freelancer'),
        ('entrepreneur', '🚀 Entrepreneur / Business Owner'),
        ('returning', '🔄 Returning to Workforce'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='job_seeker')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.email
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'