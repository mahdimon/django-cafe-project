from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from core.models import Item
from customer.models import Order

class StaffCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'is_staff']  # 'is_staff' will mark it as a staff account
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class StaffUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if 'password' in self.cleaned_data and self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'items', 'table_number', 'status']
        widgets = {
            'items': forms.CheckboxSelectMultiple(),
        }