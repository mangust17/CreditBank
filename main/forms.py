from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, CreditApplication, Document, Report

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтверждение пароля'})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone']

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Пароль'}
        )
    )

    class Meta:
        model = User
        fields = ['username', 'password']

class CreditApplicationForm(forms.ModelForm):
    class Meta:
        model = CreditApplication
        fields = ['amount', 'term_months', 'purpose']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'term_months': forms.NumberInput(attrs={'class': 'form-control'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['doc_type', 'file']
        widgets = {
            'doc_type': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
        }