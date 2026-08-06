from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from .models import Subject, Group

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, required=False, label="Пол")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        labels = {
            'username': 'Логин',
            'email': 'Электронная почта'
        } 

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']
        labels = {'name': 'Название предмета'}

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'subject', 'teacher', 'schedule']
        labels = {
            'name': 'Название группы',
            'subject': 'Предмет',
            'teacher': 'Преподаватель',
            'schedule': 'Расписание'
        }