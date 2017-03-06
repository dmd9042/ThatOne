from django import forms

class LogIn(forms.Form):
    usr = forms.CharField(label='usr', max_length=20)
    password = forms.CharField(label='pass', max_length=20)
