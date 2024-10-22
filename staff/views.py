from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StaffCreationForm, StaffUpdateForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from customer.models import Order
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

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

class StaffDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'staff/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['last_orders'] = Order.objects.all().order_by('-order_date')[:5]
        return context

@login_required
def orders_view(request):
    orders = Order.objects.all()
    return render(request, 'staff/orders.html', {'orders': orders})

@login_required
def logout_view(request):
    logout(request)
    return redirect('staff:login')

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'staff/orders.html'  # Updated to reflect the merged template
    context_object_name = 'orders'

    def get_queryset(self):
        queryset = Order.objects.all()
        status = self.request.GET.get('status')
        table_number = self.request.GET.get('table_number')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if status:
            queryset = queryset.filter(status=status)
        if table_number:
            queryset = queryset.filter(table_number=table_number)
        if start_date and end_date:
            queryset = queryset.filter(order_date__range=[start_date, end_date])

        return queryset

class OrderEditView(LoginRequiredMixin, UpdateView):
    model = Order
    fields = ['status', 'table_number']  # You can extend this based on your requirements
    template_name = 'staff/order_edit.html'
    success_url = reverse_lazy('staff:orders')

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    template_name = 'staff/order_form.html'  # Adjust the template name as needed
    fields = '__all__'  # Adjust fields as necessary

class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    template_name = 'staff/order_form.html'  # Adjust the template name as needed
    fields = '__all__'  # Adjust fields as necessary

class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = 'staff/order_confirm_delete.html'  # Adjust the template name as needed
    success_url = '/staff/orders/'  # Redirect after deletion
