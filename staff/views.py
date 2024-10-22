from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StaffCreationForm, StaffUpdateForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout

@login_required
def staff_list(request):
    staff_members = User.objects.all()
    return render(request, 'staff/staff_list.html', {'staff_members': staff_members})

@login_required
def create_staff(request):
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff account created successfully.')
            return redirect('staff:staff_list')
    else:
        form = StaffCreationForm()
    return render(request, 'staff/create_staff.html', {'form': form})

@login_required
def update_staff(request, staff_id):
    user = get_object_or_404(User, pk=staff_id)
    if request.method == 'POST':
        form = StaffUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff account updated successfully.')
            return redirect('staff:staff_list')
    else:
        form = StaffUpdateForm(instance=user)
    return render(request, 'staff/update_staff.html', {'form': form})

@login_required
def delete_staff(request, staff_id):
    user = get_object_or_404(User, pk=staff_id)
    user.delete()
    messages.success(request, 'Staff account deleted successfully.')
    return redirect('staff:staff_list')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('staff:home')
    else:
        form = AuthenticationForm()
    return render(request, 'staff/login.html', {'form': form})

@login_required
def home(request):
    return render(request, 'staff/home.html')

@login_required
def orders_view(request):
    # Your logic for handling orders goes here
    return render(request, 'orders.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('staff:login')