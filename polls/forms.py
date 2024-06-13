from django import forms


class RestaurantSearchForm(forms.Form):
    query = forms.CharField(label='',  max_length=100)
