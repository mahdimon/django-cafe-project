from django import forms
import re
from core.models import Category


class PurchaseForm(forms.Form):
    phone_number = forms.CharField(
        required=False, 
        label='Phone Number (Optional)',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter your phone number'
        })
    )
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        if phone_number:
            if not re.match(r'^09\d{9}$', phone_number): 
                raise forms.ValidationError('Please enter a valid 11-digit phone number starting with 09.')

        return phone_number 
    
class CategoryFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False, 
        label="Filter by Category",
        widget=forms.Select(attrs={'class': 'form-control'}) 
    )