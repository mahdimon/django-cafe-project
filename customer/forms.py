from django import forms

class PurchaseForm(forms.Form):
    phone_number = forms.CharField(max_length=15, label="Phone Number",required=False)
