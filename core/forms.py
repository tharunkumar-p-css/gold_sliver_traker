"""
core/forms.py — Registration, Profile, and Alert forms.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from core.models import UserProfile, UserAlert


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    telegram_chat_id = forms.CharField(
        max_length=50, required=False, 
        help_text="Optional: Enter your Telegram Chat ID to receive free instant alerts."
    )
    country = forms.CharField(max_length=100, initial='India')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            user.profile.telegram_chat_id = self.cleaned_data.get('telegram_chat_id', '')
            user.profile.country = self.cleaned_data.get('country', 'India')
            user.profile.save()
        return user


class LoginForm(AuthenticationForm):
    pass


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'country', 'currency',
                  'notification_preference', 'telegram_chat_id', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.user.first_name = self.cleaned_data['first_name']
            profile.user.last_name = self.cleaned_data['last_name']
            profile.user.email = self.cleaned_data['email']
            profile.user.save()
            profile.save()
        return profile


class AlertForm(forms.ModelForm):
    class Meta:
        model = UserAlert
        fields = ['metal', 'condition', 'percentage_threshold', 'note']
        widgets = {
            'percentage_threshold': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'max': '100'}),
            'note': forms.TextInput(attrs={'placeholder': 'Optional note…'}),
        }
        labels = {
            'percentage_threshold': 'Threshold (%)',
        }
