from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from core.models import Item

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
        return render(request, 'customer/cart.html',{'items':cart_items})

    def post(self, request, action):
        """Handle cart actions."""
        if action == "add":
            item_id = request.POST.get('item_id')
            item = get_object_or_404(Item, id=item_id)

            cart, created = ShoppingCart.objects.get_or_create(customer=request.user if request.user.is_authenticated else None)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)

            if not created:
                cart_item.quantity += 1
            cart_item.save()

        elif action == "update":
            cart_item_id = request.POST.get('cart_item_id')
            quantity = int(request.POST.get('quantity', 1))
            cart_item = get_object_or_404(CartItem, id=cart_item_id)

            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()

        elif action == "remove":
            cart_item_id = request.POST.get('cart_item_id')
            cart_item = get_object_or_404(CartItem, id=cart_item_id)
            cart_item.delete()

        return redirect('view_cart')  # Redirect to the cart view
def place_order_view(request):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '')

        # Create or get the customer (optional phone number)
        if phone_number:
            customer, created = Customer.objects.get_or_create(
                phone_number=phone_number)
        else:
            customer = None

        order = Order.objects.create(
            customer=customer,
            session_key=session_key,
            order_details=request.POST['order_details']
        )

        return redirect('order_success')

    return render(request, 'place_order.html')
