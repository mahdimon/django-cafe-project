from django import forms
from core.models import Category
from customer.models import Customer
from django.forms.widgets import DateInput

class SalesReportForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), required=False)
    time_of_day = forms.IntegerField(min_value=0, max_value=23, required=False)
    TIME_FRAME_CHOICES = [
        ('total', 'Total'),
        ('monthly', 'Monthly'),
        ('daily', 'Daily'),
        ('yearly', 'Yearly')
    ]
    time_frame = forms.ChoiceField(choices=TIME_FRAME_CHOICES, required=False, initial='total')
    


class PopularItemsForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False) 

class DateSelectionForm(forms.Form):
    selected_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Select Date")