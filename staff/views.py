from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import StaffCreationForm, StaffUpdateForm, OrderCreateForm, OrderEditForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from customer.models import Order, Customer, OrderItem
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import Item, Category
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect


@login_required
@user_passes_test(lambda u: u.is_staff)
def staff_list(request):
    staff_members = User.objects.all()
    return render(request, 'staff/staff_list.html', {'staff_members': staff_members})

@login_required
@user_passes_test(lambda u: u.is_staff)
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
@user_passes_test(lambda u: u.is_staff)
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
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # This will actually be email now
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('staff:home')
            else:
                form.add_error(None, 'Invalid email or password.')
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
    template_name = 'staff/order_form.html'
    form_class = OrderCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = Item.objects.filter(available=True)  # Make sure to filter based on availability
        return context

    def form_valid(self, form):
        # Save the form without committing the many-to-many field (items)
        order = form.save(commit=False)

        # Handle the phone number (if provided)
        phone_number = form.cleaned_data.get('phone_number')
        if phone_number:
            # Create or get the customer based on the provided phone number
            customer, created = Customer.objects.get_or_create(phone_number=phone_number)

            # Create the order but don't save it yet
            order = form.save(commit=False)
            order.customer = customer  # Link the order to the customer
        else:
            # If no phone number is provided, create the order without a customer
            order = form.save(commit=False)

            # Save the order to get the ID
            order.save()

        # Handle the many-to-many field (items) through OrderItem
        items = self.request.POST.getlist('items')  # Get the selected items
        quantities = self.request.POST.getlist('quantities')  # Assume you provide quantities for each item

        for item_id, quantity in zip(items, quantities):
            item = Item.objects.get(id=item_id)
            OrderItem.objects.create(order=order, item=item, quantity=quantity)

        # Save the order again to ensure everything is persisted
        order.save()

        return redirect(reverse_lazy('staff:orders'))  # Redirect to the orders list

class OrderEditView(LoginRequiredMixin, UpdateView):
    model = Order
    template_name = 'staff/order_form.html'  # Reuse the same template for editing
    form_class = OrderEditForm  # Use the custom form for editing
    success_url = reverse_lazy('staff:orders')  # Redirect to the orders page after editing

class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = 'staff/order_confirm_delete.html'  # Adjust the template name as needed
    success_url = reverse_lazy('staff:orders')  # Updated to use reverse_lazy

class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'staff/item_list.html'
    context_object_name = 'items'

class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    template_name = 'staff/item_form.html'
    fields = ['category', 'name', 'description', 'price', 'available']
    success_url = reverse_lazy('staff:item_list')

class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    template_name = 'staff/item_form.html'
    fields = ['category', 'name', 'description', 'price', 'available']
    success_url = reverse_lazy('staff:item_list')

class ItemDeleteView(LoginRequiredMixin, DeleteView):
    model = Item
    template_name = 'staff/item_confirm_delete.html'
    success_url = reverse_lazy('staff:item_list')

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'staff/category_list.html', {'categories': categories})

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'staff/category_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('staff:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully.')
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    template_name = 'staff/category_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('staff:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully.')
        return super().form_valid(form)

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'staff/category_confirm_delete.html'
    success_url = reverse_lazy('staff:category_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.object)  # Check if the correct object is passed
        return context