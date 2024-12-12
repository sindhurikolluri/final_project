# forms.py
from django import forms

class SelectionForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.TextField()
    price = forms.DecimalField(max_digits=10, decimal_places=2)
