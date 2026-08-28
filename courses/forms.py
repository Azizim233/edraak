from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'name-input',
            'placeholder': 'مەسىلەن: ئەھمەت ھەسەن',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'example@edraak.com',
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': '+90 5xx xxx xx xx',
        })
    )
    telegram_id = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': '@username',
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
        })
    )

    class Meta:
        model = CustomUser
        fields = ('full_name', 'email', 'phone', 'telegram_id')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('بۇ ئېلېكترونلۇق خەت ئاللىبۇرۇن تىزىملانغان.')
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 6:
            raise forms.ValidationError('پارول ئەڭ ئاز 6 ھەرپ بولۇشى كېرەك.')
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # email نى username قىلىش
        user.email = self.cleaned_data['email']
        user.full_name = self.cleaned_data['full_name']
        user.phone = self.cleaned_data['phone']
        user.telegram_id = self.cleaned_data['telegram_id']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="ئېلېكترونلۇق خەت",
        widget=forms.EmailInput(attrs={
            'placeholder': 'example@edraak.com',
        })
    )