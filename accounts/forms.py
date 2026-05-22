# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-3 py-2 border rounded-lg',
        'placeholder': 'Email address'
    }))
    full_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={
        'class': 'w-full px-3 py-2 border rounded-lg',
        'placeholder': 'Full Name'
    }))
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.Select(attrs={
        'class': 'w-full px-3 py-2 border rounded-lg'
    }))
    
    class Meta:
        model = User
        fields = ('full_name', 'email', 'role', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Use email as username
        user.first_name = self.cleaned_data['full_name'].split()[0] if ' ' in self.cleaned_data['full_name'] else self.cleaned_data['full_name']
        user.last_name = ' '.join(self.cleaned_data['full_name'].split()[1:]) if ' ' in self.cleaned_data['full_name'] else ''
        if commit:
            user.save()
        return user