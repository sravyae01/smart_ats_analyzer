# accounts/views.py - COMPLETE ERROR-FREE VERSION
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User

def signup_view(request):
    """User signup page - FREE forever"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '')
        email = request.POST.get('email', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        role = request.POST.get('role', 'job_seeker')
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'accounts/signup.html')
        
        if len(password1) < 6:
            messages.error(request, 'Password must be at least 6 characters')
            return render(request, 'accounts/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'accounts/signup.html')
        
        # Split full name into first and last name
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        
        login(request, user)
        
        # Custom success message based on role
        role_messages = {
            'job_seeker': 'Start applying to your dream jobs!',
            'fresher': 'Kickstart your career with a great resume!',
            'student': 'Build a strong resume for internships!',
            'experienced': 'Take your career to the next level!',
            'career_changer': 'Showcase your transferable skills!',
            'internship': 'Land the perfect internship!',
            'recruiter': 'Find the best candidates efficiently!',
            'freelancer': 'Attract more clients with a professional resume!',
            'entrepreneur': 'Build your personal brand!',
            'returning': 'Welcome back to the workforce!'
        }
        
        custom_message = role_messages.get(role, 'Start analyzing your resume for FREE!')
        messages.success(request, f'🎉 Welcome {full_name}! {custom_message} Unlimited analyses forever.')
        return redirect('dashboard:home')
    
    return render(request, 'accounts/signup.html')


def login_view(request):
    """User login page"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'✨ Welcome back {user.email}! Ready to optimize your resume?')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')  # ← Now redirects to landing page

@login_required
def profile_view(request):
    """User profile page - FREE for all users"""
    if request.method == 'POST':
        # Update profile
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone_number = request.POST.get('phone_number', '')
        
        if first_name:
            request.user.first_name = first_name
        if last_name:
            request.user.last_name = last_name
        if phone_number:
            request.user.phone_number = phone_number
        
        request.user.save()
        messages.success(request, '✅ Profile updated successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile.html', {'user': request.user})