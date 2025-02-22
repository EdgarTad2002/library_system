
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class RegisterUsersForm(UserCreationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={'autocomplete': 'off', 'value': ''}))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput())
    data_birth = forms.DateField(label="Дата рождения", widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name', 'data_birth', 'phone', 'password1', 'password2']
        labels = {
            "email": "E-mail",
            "first_name": "Имя",
            "last_name": "Фамилия",
        }

        widgets  = {
            'email': forms.TextInput(),
            'first_name': forms.TextInput(),
            'last_name':  forms.TextInput(),
            'phone': forms.TextInput(),
        }