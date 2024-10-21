from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from core.models import Item
from .forms import PurchaseForm
from .models import Customer ,Order,OrderItem

class Menu(View):
    def get(self , request):
        if not request.session.session_key:
            request.session.create()
        items = Item.objects.filter(available=True)
        return render(request,"customer/menu.html",{'items':items})
class Cart(View):
    def get(self, request):
        cart_item_ids = map(int, request.session.get('cart', {}).keys())
        cart_items = Item.objects.filter(id__in=cart_item_ids)
        form = PurchaseForm()
        return render(request, 'customer/cart.html',{'items':cart_items, "form":form})

def post(self, request, action):
    form = PurchaseForm(request.POST)
    if action == "buy" and form.is_valid():
        cart = request.session.get('cart', {})
        phone_number = form.cleaned_data.get('phone_number', None)

        customer_id = request.session.get('customer_id')
    
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                customer = None  
        

        if not customer:
            customer, created = Customer.objects.get_or_create(phone_number=phone_number)
            request.session['customer_id'] = customer.pk  # Store new customer ID in session

        # Create the order
        order = Order.objects.create(customer=customer)

        for item_id, quantity in cart.items():
            item = Item.objects.filter(id=item_id).first()
            if not item:
                continue
            OrderItem.objects.create(order=order, item=item, quantity=quantity)

        request.session['cart'] = {}  # Clear the cart after purchase

        return redirect('customer/success.html', order_id=order.id)

    else:
        self.get(request)
        
 
def success(request):
    pass