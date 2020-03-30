from django import forms

from .models import User

class UserLoginForm(forms.ModelForm):

    class Meta:
        password = forms.CharField(widget=forms.PasswordInput)
        model = User
        widgets = {
            'password' : forms.PasswordInput(),
        }
        fields = ('email', 'password')
