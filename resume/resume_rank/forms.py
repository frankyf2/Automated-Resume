from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import JobDescription

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class JobForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = ['title', 'company', 'required_skills', 'education_level', 'experiences_years', 'description']
