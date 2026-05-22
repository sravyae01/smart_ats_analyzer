# analyzer/admin.py - COMPLETE WORKING VERSION
from django.contrib import admin
from django.utils.html import format_html
from .models import Analysis, ResumeVersion, HeatmapData, RewriteSuggestion

# ============================================
# Analysis Admin
# ============================================
@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    """Admin configuration for Analysis model"""
    
    list_display = (
        'id', 
        'user_email', 
        'ats_score_display', 
        'status_badge', 
        'processing_time',
        'created_at'
    )
    
    # ✅ Fixed: Removed admin.RangeFilter
    list_filter = ('status', 'created_at', 'updated_at')
    
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'job_title', 'job_description')
    
    readonly_fields = ('id', 'created_at', 'updated_at', 'processing_time', 'resume_text_preview')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'status', 'created_at', 'updated_at')
        }),
        ('Resume & Job', {
            'fields': ('resume_file', 'job_title', 'job_description', 'resume_text_preview')
        }),
        ('Scores (0-100)', {
            'fields': ('ats_score', 'critical_skills_match', 'skills_match', 'profile_match', 'format_score'),
        }),
        ('Keyword Analysis', {
            'fields': ('found_keywords', 'missing_keywords', 'critical_skills'),
            'classes': ('collapse',)
        }),
        ('Technical Details', {
            'fields': ('processing_time',),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
    list_per_page = 25
    
    def user_email(self, obj):
        """Display user email with link to user admin"""
        from django.urls import reverse
        from django.utils.safestring import mark_safe
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return mark_safe(f'<a href="{url}">{obj.user.email}</a>')
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def ats_score_display(self, obj):
        """Display ATS score with color coding"""
        color = 'red'
        if obj.ats_score >= 70:
            color = 'green'
        elif obj.ats_score >= 50:
            color = 'orange'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, obj.ats_score
        )
    ats_score_display.short_description = 'ATS Score'
    ats_score_display.admin_order_field = 'ats_score'
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'pending': 'gray',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    def resume_text_preview(self, obj):
        """Show preview of extracted resume text"""
        if obj.resume_text:
            preview = obj.resume_text[:500]
            if len(obj.resume_text) > 500:
                preview += '...'
            return format_html(
                '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px; font-family: monospace; max-height: 200px; overflow: auto;">{}</div>',
                preview.replace('\n', '<br>')
            )
        return 'No text extracted yet'
    resume_text_preview.short_description = 'Resume Text Preview'
    
    actions = ['reprocess_analysis', 'export_selected_analyses']
    
    def reprocess_analysis(self, request, queryset):
        """Re-process selected analyses"""
        for analysis in queryset:
            analysis.status = 'pending'
            analysis.save()
        self.message_user(request, f'Re-processing {queryset.count()} analysis(es)')
    reprocess_analysis.short_description = "Re-process selected analyses"
    
    def export_selected_analyses(self, request, queryset):
        """Export selected analyses as CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="analyses_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'User Email', 'ATS Score', 'Status', 'Created At', 'Missing Keywords Count'])
        
        for analysis in queryset:
            writer.writerow([
                str(analysis.id),
                analysis.user.email,
                analysis.ats_score,
                analysis.status,
                analysis.created_at,
                len(analysis.missing_keywords)
            ])
        
        return response
    export_selected_analyses.short_description = "Export selected analyses to CSV"

# ============================================
# ResumeVersion Admin
# ============================================
@admin.register(ResumeVersion)
class ResumeVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'version_number', 'ats_score_display', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'content')
    readonly_fields = ('id', 'created_at')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    
    def ats_score_display(self, obj):
        color = 'green' if obj.ats_score >= 70 else 'orange' if obj.ats_score >= 50 else 'red'
        return format_html('<span style="color: {};">{}%</span>', color, obj.ats_score)
    ats_score_display.short_description = 'ATS Score'

# ============================================
# HeatmapData Admin
# ============================================
@admin.register(HeatmapData)
class HeatmapDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'analysis_info', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('analysis__user__email',)
    readonly_fields = ('id', 'created_at')
    
    def analysis_info(self, obj):
        return f"{obj.analysis.user.email} - {obj.analysis.created_at.date()}"
    analysis_info.short_description = 'Analysis'

# ============================================
# RewriteSuggestion Admin
# ============================================
@admin.register(RewriteSuggestion)
class RewriteSuggestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'analysis_info', 'keyword_added', 'accepted', 'created_at')
    list_filter = ('accepted', 'created_at')
    search_fields = ('keyword_added', 'analysis__user__email')
    readonly_fields = ('id', 'created_at')
    
    def analysis_info(self, obj):
        return f"{obj.analysis.user.email}"
    analysis_info.short_description = 'User'