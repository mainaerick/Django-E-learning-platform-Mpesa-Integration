from django.db.models.base import Model
from django.forms import ModelForm, fields
from .models import User
from django.contrib.auth.forms import UserCreationForm


class MyUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']


class UserForm(ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'phone']
