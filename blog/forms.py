from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import *


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(max_length=250, required=True)
    password = forms.CharField(
        label="Password", strip=False, required=True, widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        # Попытка аутентификации по username или email
        user = User.objects.filter(
            models.Q(username=username) | models.Q(email=username)).first()

        if user and user.check_password(password):
            self.user_cache = user
        else:
            raise forms.ValidationError("Invalid login credentials")
