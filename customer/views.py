from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from core.models import Item
from .forms import PurchaseForm
from .models import Customer ,Order,OrderItem
import json

class Menu(View):
    def get(self , request):
        if not request.session.session_key:
            request.session.create()
        items = Item.objects.filter(available=True)
        return render(request,"customer/menu.html",{'menu_items':items})
class Cart(View):
    def get(self, request):
        cart_cookie = request.COOKIES.get('cart', '{}')
        cart = json.loads(cart_cookie)
        cart_item_ids = list(map(int, cart.keys()))
        cart_items = Item.objects.filter(id__in=cart_item_ids)
        form = PurchaseForm()
        cart = {int(key): str(value) for key, value in cart.items()}
        return render(request, 'customer/cart.html',{'cart_items':cart_items, "form":form,'cart':cart})

    def post(self, request):
        form = PurchaseForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number', None)
            customer_id = request.session.get('customer_id')
            cart_cookie = request.COOKIES.get('cart',{})
            cart = json.loads(cart_cookie)
            customer = None
            if customer_id:
                
                try:
                    customer = Customer.objects.get(id=customer_id)
                except Customer.DoesNotExist:
                    customer = None  
            

            if not customer:
                customer, created = Customer.objects.get_or_create(phone_number=phone_number)
                customer.save()
                request.session['customer_id'] = customer.pk 

            
            order = Order.objects.create(customer=customer)
            
            order.price = 0
            order.save()
            for item_id, quantity in cart.items():
                item = Item.objects.get(id=item_id)
                if not item or quantity < 1:
                    continue
                order.price += int(item.price)*quantity
                OrderItem.objects.create(order=order, item=item, quantity=quantity)
            
            order.save()
            response = redirect('checkout',order_id = order.id) 
            response.delete_cookie("cart")

            return response

        else:
            self.get(request)
            
    
def checkout(request,order_id):
    return render(request,"customer/checkout.html",{'order_id':order_id})

def history(request):
    customer_id = request.session.get('customer_id')
    if customer_id:
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            customer = None 
    orders = customer.orders
    render("history",{'orders':orders})