from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username",)

    def save(self, commit=True, first_name=first_name, last_name=last_name):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.first_name = first_name
        user.last_name = last_name
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class RestaurantSearchForm(forms.Form):
    query = forms.CharField(label='',  max_length=100)
