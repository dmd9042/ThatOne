from django import forms

from Home.models import User

class EditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('fName','lName','phone','email','birthday')