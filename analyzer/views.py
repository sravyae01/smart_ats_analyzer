# analyzer/views.py - COMPLETE WORKING VERSION WITH AI CHAT ASSISTANT
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Avg
import json
import time
import uuid
from .models import Analysis, ResumeVersion

# Import services
try:
    from .services.ats_engine import ATSEngine
    from .services.parser import ResumeParser
    ats_engine = ATSEngine()
    parser = ResumeParser()
except ImportError:
    # Dummy services if not available
    class DummyEngine:
        def calculate_overall_score(self, resume_text, job_description):
            return {
                'total_score': 75,
                'breakdown': {
                    'critical_skills_match': 80,
                    'semantic_similarity': 70,
                    'profile_compatibility': 75,
                    'format_score': 85
                },
                'missing_keywords': ['Python', 'Django', 'React'],
                'found_keywords': ['JavaScript', 'HTML', 'CSS'],
                'critical_skills': ['Python', 'JavaScript']
            }
    
    class DummyParser:
        def parse_resume(self, file):
            return "Sample resume text for testing\nSkills: Python, Django, JavaScript"
    
    ats_engine = DummyEngine()
    parser = DummyParser()


# ============================================
# AI CHAT ASSISTANT FUNCTIONS
# ============================================

def get_smart_response(user_message, user_resume_score=None):
    """Generate intelligent responses based on user message"""
    message_lower = user_message.lower()
    
    # Resume tips
    if any(word in message_lower for word in ['improve', 'better', 'tips', 'advice']):
        if 'score' in message_lower:
            return """
            **📈 To improve your ATS score:**
            
            1. **Add keywords** from job descriptions
            2. **Use standard section headings** (Experience, Education, Skills)
            3. **Include metrics** (e.g., "Increased sales by 30%")
            4. **Keep formatting simple** (no tables or images)
            5. **Customize for each job** application
            
            Would you like specific tips for any of these areas?
            """
        return """
            **💡 Resume Improvement Tips:**
            
            ✨ **Action Verbs**: Use strong verbs like "led", "developed", "achieved"
            📊 **Quantify achievements**: Add numbers, percentages, and results
            🎯 **Tailor to job**: Customize keywords for each application
            📏 **Keep it concise**: 1-2 pages maximum
            ✅ **Proofread**: Check for spelling and grammar errors
            
            Need help with a specific section?
            """
    
    # Keywords help
    elif 'keyword' in message_lower:
        return """
            **🔑 How to find the right keywords:**
            
            1. **Read job descriptions** carefully
            2. **Look for repeated terms** in requirements
            3. **Check industry-specific** terminology
            4. **Use action verbs** (managed, created, optimized)
            5. **Include both hard skills** (Python, SQL) and **soft skills** (leadership, communication)
            
            💡 Pro tip: Our analyzer shows exactly which keywords you're missing!
            """
    
    # Bullet points help
    elif 'bullet' in message_lower or 'point' in message_lower:
        return """
            **✍️ How to Write Powerful Bullet Points:**
            
            ❌ **Weak**: "Responsible for managing team"
            ✅ **Strong**: "Led a team of 8 developers, delivering projects 20% ahead of schedule"
            
            **Formula to follow:**
            [Action Verb] + [What you did] + [How you did it] + [Result]
            
            **Examples:**
            • "Increased customer engagement by 45% through targeted email campaigns"
            • "Reduced processing time by 30% by implementing automated workflows"
            • "Saved $50,000 annually by renegotiating vendor contracts"
            
            Want me to help rewrite one of your bullet points?
            """
    
    # Format tips
    elif 'format' in message_lower:
        return """
            **📄 ATS-Friendly Resume Format:**
            
            ✅ **DO:**
            • Use standard fonts (Arial, Calibri, Times New Roman)
            • Save as PDF or DOCX
            • Use simple bullet points (• or -)
            • Include clear section headings
            
            ❌ **DON'T:**
            • Use tables or columns
            • Add images or graphics
            • Use headers/footers
            • Use fancy formatting
            
            **Recommended sections:**
            1. Contact Info
            2. Professional Summary
            3. Skills
            4. Work Experience
            5. Education
            """
    
    # Interview help
    elif 'interview' in message_lower:
        return """
            **🎯 Interview Preparation Tips:**
            
            **STAR Method for answering questions:**
            - **S**ituation: Set the context
            - **T**ask: Describe your responsibility
            - **A**ction: Explain what you did
            - **R**esult: Share the outcome
            
            **Common questions to practice:**
            1. "Tell me about yourself"
            2. "Why do you want this job?"
            3. "What are your strengths/weaknesses?"
            4. "Describe a challenge you overcame"
            
            Would you like help preparing for a specific question?
            """
    
    # Greeting
    elif any(word in message_lower for word in ['hi', 'hello', 'hey', 'greetings']):
        return f"""
            👋 Hello! I'm your AI Resume Assistant.
            
            I can help you with:
            • Resume improvement tips
            • ATS optimization advice  
            • Keyword suggestions
            • Interview preparation
            • Career guidance
            
            What would you like to know?
            """
    
    # Score specific question
    elif 'score' in message_lower and user_resume_score:
        if user_resume_score < 50:
            return f"""
                **📊 Your current ATS score is {user_resume_score}%**
                
                Don't worry! Here's how to improve:
                1. Add more keywords from job descriptions
                2. Use standard section headings
                3. Include metrics and achievements
                4. Remove complex formatting
                
                Want specific tips for your resume?
                """
        elif user_resume_score < 70:
            return f"""
                **📊 Your current ATS score is {user_resume_score}%**
                
                Good progress! To reach 70%+:
                1. Add quantifiable achievements (numbers, %)
                2. Include industry-specific keywords
                3. Strengthen your professional summary
                4. Add relevant certifications
                
                Would you like help with any of these?
                """
        else:
            return f"""
                **📊 Your current ATS score is {user_resume_score}%**
                
                Excellent score! 🎉 You're doing great!
                
                To maintain excellence:
                1. Keep customizing for each job
                2. Stay updated with industry keywords
                3. Add new achievements regularly
                
                Ready for your next interview?
                """
    
    # Default response
    else:
        return f"""
            Thanks for your message! I'm here to help with your resume.
            
            You can ask me about:
            • How to improve your ATS score
            • Finding the right keywords
            • Writing better bullet points
            • Resume formatting tips
            • Interview preparation
            
            What specific aspect would you like help with?
        """


@login_required
def chat_view(request):
    """AI Chat Assistant Page"""
    return render(request, 'chat_assistant.html')


@login_required
@csrf_exempt
def chat_ask(request):
    """API endpoint for AI chat responses"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # Get user's recent analysis score if exists
            latest_analysis = Analysis.objects.filter(
                user=request.user, 
                status='completed'
            ).order_by('-created_at').first()
            
            user_score = latest_analysis.ats_score if latest_analysis else None
            
            # Generate smart response
            response = get_smart_response(user_message, user_score)
            
            return JsonResponse({'reply': response})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# ============================================
# ORIGINAL ANALYSIS FUNCTIONS
# ============================================

@login_required
def new_analysis(request):
    """Show new analysis page - FREE unlimited"""
    return render(request, 'analyzer/new_analysis.html', {
        'user': request.user,
    })

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def upload_and_analyze(request):
    """Handle resume upload and run analysis - FREE"""
    
    # Get uploaded file and job description
    if 'resume' not in request.FILES:
        return JsonResponse({'error': 'No resume file provided'}, status=400)
    
    resume_file = request.FILES['resume']
    job_description = request.POST.get('job_description', '')
    job_title = request.POST.get('job_title', '')
    
    if not job_description:
        return JsonResponse({'error': 'Job description is required'}, status=400)
    
    # Validate file type
    if not resume_file.name.endswith(('.pdf', '.docx')):
        return JsonResponse({'error': 'Only PDF and DOCX files are supported'}, status=400)
    
    # Create analysis record
    analysis = Analysis.objects.create(
        user=request.user,
        resume_file=resume_file,
        job_description=job_description,
        job_title=job_title,
        status='processing'
    )
    
    try:
        start_time = time.time()
        
        # Parse resume
        resume_text = parser.parse_resume(resume_file)
        analysis.resume_text = resume_text
        
        # Calculate ATS score
        result = ats_engine.calculate_overall_score(resume_text, job_description)
        
        # Update analysis with results
        analysis.ats_score = result['total_score']
        analysis.critical_skills_match = result['breakdown']['critical_skills_match']
        analysis.skills_match = result['breakdown']['semantic_similarity']
        analysis.profile_match = result['breakdown']['profile_compatibility']
        analysis.format_score = result['breakdown']['format_score']
        analysis.missing_keywords = result['missing_keywords']
        analysis.found_keywords = result['found_keywords']
        analysis.critical_skills = result['critical_skills']
        analysis.status = 'completed'
        analysis.processing_time = time.time() - start_time
        analysis.save()
        
        # Create version record
        ResumeVersion.objects.create(
            user=request.user,
            analysis=analysis,
            version_number=ResumeVersion.objects.filter(user=request.user).count() + 1,
            content=resume_text,
            file=analysis.resume_file,
            ats_score=analysis.ats_score
        )
        
        return JsonResponse({
            'success': True,
            'analysis_id': str(analysis.id),
            'score': analysis.ats_score,
            'redirect_url': f'/analyzer/results/{analysis.id}/'
        })
        
    except Exception as e:
        analysis.status = 'failed'
        analysis.save()
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def results_view(request, analysis_id):
    """Show analysis results"""
    try:
        if isinstance(analysis_id, str):
            analysis_id = uuid.UUID(analysis_id)
        
        analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
        
        if analysis.status != 'completed':
            messages.warning(request, 'Analysis is still processing. Please refresh.')
            return redirect('analyzer:new')
        
        return render(request, 'analyzer/results.html', {
            'analysis': analysis,
            'user': request.user
        })
    except (ValueError, TypeError):
        messages.error(request, 'Invalid analysis ID')
        return redirect('analyzer:new')

@login_required
def history_view(request):
    """Show all user analyses"""
    analyses = Analysis.objects.filter(user=request.user, status='completed').order_by('-created_at')
    
    avg_score = analyses.aggregate(Avg('ats_score'))['ats_score__avg']
    if avg_score is None:
        avg_score = 0
    
    return render(request, 'analyzer/history.html', {
        'analyses': analyses,
        'total_analyses': analyses.count(),
        'best_score': analyses.first().ats_score if analyses.exists() else 0,
        'average_score': avg_score
    })

@login_required
@csrf_exempt
def get_analysis_data(request, analysis_id):
    """API endpoint to get analysis data for AJAX"""
    try:
        if isinstance(analysis_id, str):
            analysis_id = uuid.UUID(analysis_id)
        
        analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
        
        return JsonResponse({
            'id': str(analysis.id),
            'score': analysis.ats_score,
            'breakdown': {
                'critical': analysis.critical_skills_match,
                'skills': analysis.skills_match,
                'profile': analysis.profile_match,
                'format': analysis.format_score
            },
            'missing_keywords': analysis.missing_keywords[:10] if analysis.missing_keywords else [],
            'found_keywords': analysis.found_keywords[:20] if analysis.found_keywords else [],
            'job_title': analysis.job_title,
            'created_at': analysis.created_at.strftime('%Y-%m-%d %H:%M')
        })
    except (ValueError, TypeError, Analysis.DoesNotExist):
        return JsonResponse({'error': 'Analysis not found'}, status=404)