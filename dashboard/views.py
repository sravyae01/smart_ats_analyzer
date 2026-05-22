# dashboard/views.py - COMPLETE FREE VERSION
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max
from django.core.paginator import Paginator
from django.http import JsonResponse
from analyzer.models import Analysis

@login_required
def dashboard_home(request):
    """Main dashboard view - FREE unlimited"""
    user = request.user
    
    # Get user's analyses (first 5 for initial load)
    analyses = Analysis.objects.filter(user=user, status='completed').order_by('-created_at')[:5]
    
    # Calculate statistics
    total_analyses = Analysis.objects.filter(user=user, status='completed').count()
    
    avg_score = Analysis.objects.filter(user=user, status='completed').aggregate(Avg('ats_score'))['ats_score__avg']
    if avg_score is None:
        avg_score = 0
    
    best_score = Analysis.objects.filter(user=user, status='completed').aggregate(Max('ats_score'))['ats_score__max']
    if best_score is None:
        best_score = 0
    
    # Total resumes analyzed across all users
    total_resumes_analyzed = Analysis.objects.filter(status='completed').count()
    
    stats = {
        'total_analyses': total_analyses,
        'average_score': avg_score,
        'best_score': best_score,
        'total_resumes_analyzed': total_resumes_analyzed,
    }
    
    context = {
        'user': user,
        'analyses': analyses,
        'stats': stats,
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required
def get_more_analyses(request):
    """API endpoint for infinite scroll"""
    page_number = request.GET.get('page', 1)
    analyses_list = Analysis.objects.filter(user=request.user, status='completed').order_by('-created_at')
    
    paginator = Paginator(analyses_list, 5)
    
    try:
        page_obj = paginator.get_page(page_number)
    except Exception:
        return JsonResponse({'analyses': [], 'has_next': False})
    
    data = []
    for analysis in page_obj:
        if analysis.ats_score >= 70:
            score_color = 'text-green-600'
        elif analysis.ats_score >= 50:
            score_color = 'text-yellow-600'
        else:
            score_color = 'text-red-600'
        
        data.append({
            'id': str(analysis.id),
            'date': analysis.created_at.strftime("%b %d, %Y"),
            'score': analysis.ats_score,
            'score_color': score_color,
            'missing_keywords': analysis.missing_keywords[:3] if analysis.missing_keywords else [],
        })
    
    return JsonResponse({
        'analyses': data,
        'has_next': page_obj.has_next() if page_obj else False
    })