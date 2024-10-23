from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from core.models import Item
from customer.models import Order, Customer

class StaffCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    is_staff = forms.BooleanField(required=False, label='Is Staff', widget=forms.CheckboxInput())

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'is_staff']  # Email instead of username, with is_staff option

    def save(self, commit=True):
        user = super(StaffCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Optional: use email as username
        user.is_staff = self.cleaned_data['is_staff']  # Allows setting is_staff from the form
        if commit:
            user.save()
        return user

class StaffUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}), help_text='Leave blank if no change.')
    is_staff = forms.BooleanField(required=False, label='Is Staff', widget=forms.CheckboxInput())

    class Meta:
        model = User
        fields = ['email', 'password', 'is_staff']  # Use email instead of username, and add is_staff
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if 'password' in self.cleaned_data and self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])  # Hash the new password if provided
        user.username = self.cleaned_data['email']  # Ensure the username is the email
        user.is_staff = self.cleaned_data['is_staff']  # Update is_staff based on form input
        if commit:
            user.save()
        return user
    
class OrderCreateForm(forms.ModelForm):
    phone_number = forms.CharField(
        required=False, 
        max_length=15, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional Phone Number'})
    )
    
    # Adding items field to the form with checkboxes for each item
    items = forms.ModelMultipleChoiceField(
        queryset=Item.objects.filter(available=True),  # Assuming only available items are shown
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
    )

    class Meta:
        model = Order
        fields = ['table_number', 'status']  # Exclude customer since phone_number handles it
        widgets = {
            'table_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        # Get the order object but don't save it yet
        order = super().save(commit=False)

        # Handle the phone number and customer association
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:  # If a phone number is provided, create or update the customer
            customer, created = Customer.objects.get_or_create(phone_number=phone_number)
            order.customer = customer  # Link order to customer

        if commit:
            order.save()  # Save the order first to assign an ID
        return order


class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['items', 'table_number', 'status']  # Include fields that can be edited
        widgets = {
            'items': forms.CheckboxSelectMultiple(),
            'table_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }