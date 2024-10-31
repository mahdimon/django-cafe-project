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
from django.db import transaction
from django.core.exceptions import ValidationError

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
    template_name = 'staff/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        queryset = Order.objects.all()
        status = self.request.GET.get('status')
        table_number = self.request.GET.get('table_number')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        phone_number = self.request.GET.get('phone_number')

        if status:
            queryset = queryset.filter(status=status)
        if table_number:
            queryset = queryset.filter(table_number=table_number)
        if start_date and end_date:
            queryset = queryset.filter(order_date__range=[start_date, end_date])
        if phone_number:
            queryset = queryset.filter(phone_number__icontains=phone_number)

        return queryset




class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    template_name = 'staff/order_form.html'
    form_class = OrderCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = Item.objects.filter(available=True)
        return context

    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Create the order without saving yet
                order = form.save(commit=False)
                
                # Handle customer creation/assignment
                phone_number = form.cleaned_data.get('phone_number')
                if phone_number:
                    customer, created = Customer.objects.get_or_create(
                        phone_number=phone_number
                    )
                    order.customer = customer

                # Save the order first
                order.save()

                # Get selected items and their quantities
                selected_items = self.request.POST.getlist('items')
                quantities = self.request.POST.getlist('quantities')
                
                # Filter out quantities for unselected items
                selected_quantities = []
                for i, item_id in enumerate(selected_items):
                    if i < len(quantities):
                        selected_quantities.append(quantities[i])
                
                # Now selected_items and selected_quantities should have the same length
                if len(selected_items) == 0:
                    raise ValidationError("لطفاً حداقل یک آیتم انتخاب کنید")

                if len(selected_items) != len(selected_quantities):
                    raise ValidationError(
                        f"خطا در داده‌های ارسالی: تعداد آیتم‌ها ({len(selected_items)}) "
                        f"و مقادیر ({len(selected_quantities)}) همخوانی ندارند"
                    )

                # Create order items
                order_items = []
                for item_id, quantity in zip(selected_items, selected_quantities):
                    try:
                        quantity = int(quantity)
                        if quantity <= 0:
                            raise ValidationError(
                                f"مقدار برای آیتم {item_id} باید بیشتر از صفر باشد"
                            )
                    except ValueError:
                        raise ValidationError(
                            f"مقدار نامعتبر برای آیتم {item_id}"
                        )

                    try:
                        item = Item.objects.get(id=item_id, available=True)
                    except Item.DoesNotExist:
                        raise ValidationError(
                            f"آیتم با شناسه {item_id} موجود نیست یا در دسترس نیست"
                        )

                    order_items.append(
                        OrderItem(
                            order=order,
                            item=item,
                            quantity=quantity
                        )
                    )

                # Bulk create order items
                OrderItem.objects.bulk_create(order_items)

                return redirect(reverse_lazy('staff:orders'))

        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, f"خطا در ثبت سفارش: {str(e)}")
            return self.form_invalid(form)


class OrderEditView(LoginRequiredMixin, UpdateView):
    model = Order
    template_name = 'staff/order_form.html'  
    form_class = OrderEditForm
    success_url = reverse_lazy('staff:orders')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = Item.objects.filter(available=True)
        
        # Get current order items and their quantities
        order_items = OrderItem.objects.filter(order=self.object).select_related('item')
        context['order_items'] = {
            oi.item.id: oi.quantity for oi in order_items
        }
        return context

    def form_valid(self, form):
        try:
            with transaction.atomic():
                order = form.save(commit=False)
                
                # Handle phone number update if provided
                phone_number = form.cleaned_data.get('phone_number')
                if phone_number:
                    customer, created = Customer.objects.get_or_create(
                        phone_number=phone_number
                    )
                    order.customer = customer

                order.save()

                # Get selected items and quantities
                selected_items = self.request.POST.getlist('items')
                quantities = self.request.POST.getlist('quantities')
                
                # Filter out quantities for unselected items
                selected_quantities = []
                for i, item_id in enumerate(selected_items):
                    if i < len(quantities):
                        selected_quantities.append(quantities[i])

                if len(selected_items) == 0:
                    raise ValidationError("لطفاً حداقل یک آیتم انتخاب کنید")

                if len(selected_items) != len(selected_quantities):
                    raise ValidationError(
                        f"خطا در داده‌های ارسالی: تعداد آیتم‌ها ({len(selected_items)}) "
                        f"و مقادیر ({len(selected_quantities)}) همخوانی ندارند"
                    )

                # Delete existing order items
                OrderItem.objects.filter(order=order).delete()

                # Create new order items
                order_items = []
                for item_id, quantity in zip(selected_items, selected_quantities):
                    try:
                        quantity = int(quantity)
                        if quantity <= 0:
                            raise ValidationError(
                                f"مقدار برای آیتم {item_id} باید بیشتر از صفر باشد"
                            )
                    except ValueError:
                        raise ValidationError(
                            f"مقدار نامعتبر برای آیتم {item_id}"
                        )

                    try:
                        item = Item.objects.get(id=item_id, available=True)
                    except Item.DoesNotExist:
                        raise ValidationError(
                            f"آیتم با شناسه {item_id} موجود نیست یا در دسترس نیست"
                        )

                    order_items.append(
                        OrderItem(
                            order=order,
                            item=item,
                            quantity=quantity
                        )
                    )

                # Bulk create new order items
                OrderItem.objects.bulk_create(order_items)

                return redirect(self.success_url)

        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, f"خطا در ویرایش سفارش: {str(e)}")
            return self.form_invalid(form)
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
    fields = ['category', 'name', 'description', 'price', 'available', 'image']
    success_url = reverse_lazy('staff:item_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['image'].widget.attrs.update({'class': 'form-control'})  # اضافه کردن ویژگی به فیلد image
        return form
class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    template_name = 'staff/item_form.html'
    fields = ['category', 'name', 'description', 'price', 'available', 'image']
    success_url = reverse_lazy('staff:item_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['image'].widget.attrs.update({'class': 'form-control'})
        return form
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