from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.contrib import messages
from decimal import Decimal
from core.models import Item
from .forms import PurchaseForm ,CategoryFilterForm
from .models import Customer ,Order,OrderItem
import json
import logging

logger = logging.getLogger(__name__)

class Menu(View):
    def get(self , request):
        if not request.session.session_key:
            request.session.create()
        form = CategoryFilterForm(request.GET or None)
        items = Item.objects.filter(available=True)
        if form.is_valid():
            category = form.cleaned_data.get('category')
            if category:
                items = items.filter(category=category)
        
        return render(request,"customer/menu.html",{'menu_items':items,'form':form})
class Cart(View):
    def get_cart_data(self, request):
        try:
            cart_cookie = request.COOKIES.get('cart', '{}')
            cart = json.loads(cart_cookie)
            return {int(key): int(value) for key, value in cart.items()}
        except :
            return {}
            
    def get(self, request):
        try:
            cart = self.get_cart_data(request)
            cart_item_ids = list(cart.keys())
            cart_items = Item.objects.filter(id__in=cart_item_ids)
            form = PurchaseForm()
            
            context = {
                'cart_items': cart_items,
                'form': form,
                'cart': cart
            }
            return render(request, 'customer/cart.html', context)
            
        except Exception as e:
            messages.error(request, "خطا در نمایش سبد خرید")
            return render(request, 'customer/cart.html', {'error': str(e)})

    def post(self, request):
        try:
            form = PurchaseForm(request.POST)
            if not form.is_valid():
                messages.error(request, "لطفا اطلاعات فرم را به درستی وارد کنید")
                return self.get(request)

            cart = self.get_cart_data(request)
            if not cart:
                messages.error(request, "سبد خرید شما خالی است")
                return self.get(request)

           
            phone_number = form.cleaned_data.get('phone_number')
            customer_id = request.session.get('customer_id')
            
            customer = None
            if customer_id:
                try:
                    customer = Customer.objects.get(id=customer_id)
                except Customer.DoesNotExist:
                    customer = None
            
            if not customer:
                customer, created = Customer.objects.get_or_create(phone_number=phone_number)
                request.session['customer_id'] = customer.pk

            
            order = Order.objects.create(
                customer=customer,
                price=Decimal('0.00')
            )

           
            total_price = Decimal('0.00')
            for item_id, quantity in cart.items():
                try:
                    item = Item.objects.get(id=item_id)
                    if quantity < 1:
                        continue
                        
                    OrderItem.objects.create(
                        order=order,
                        item=item,
                        quantity=quantity
                    )
                    item_price = Decimal(str(item.price)) * quantity
                    total_price += item_price
                except Item.DoesNotExist:
                    continue

            order.price = total_price
            order.save()

            response = redirect('checkout', order_id=order.id)
            response.delete_cookie("cart")
            messages.success(request, "سفارش شما با موفقیت ثبت شد")
            return response

        except Exception as e:
            messages.error(request, "خطا در ثبت سفارش")
            return self.get(request)

def checkout(request,order_id):
    return render(request,"customer/checkout.html",{'order_id':order_id})

def history(request):
    customer_id = request.session.get('customer_id')
    orders = None
    if customer_id:
        try:
            customer = Customer.objects.get(id=customer_id)
            orders = customer.orders.all()
        except Customer.DoesNotExist:
            pass
    return render(request,"customer/history.html",{'orders':orders})