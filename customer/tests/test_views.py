from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from customer.models import Customer, Order, OrderItem
from core.models import Item
import json

class MenuViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.item1 = Item.objects.create(name="Latte", available=True, price=4.50)
        self.item2 = Item.objects.create(name="Espresso", available=True, price=3.00)

    def test_menu_view_with_items(self):
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.item1, response.context['menu_items'])
        self.assertIn(self.item2, response.context['menu_items'])

class CartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.item1 = Item.objects.create(name="Latte", price=4.50)
        self.item2 = Item.objects.create(name="Espresso", price=3.00)

    def test_cart_view_empty_cart(self):
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cart_items'].count(), 0)

    def test_cart_view_with_items_in_cart(self):
        cart_data = {str(self.item1.id): 2, str(self.item2.id): 1}
        self.client.cookies['cart'] = json.dumps(cart_data)
        
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cart'][int(self.item1.id)], 2)
        self.assertEqual(response.context['cart'][int(self.item2.id)], 1)

    def test_cart_post_order_creation(self):
        cart_data = {str(self.item1.id): 2, str(self.item2.id): 1}
        self.client.cookies['cart'] = json.dumps(cart_data)
        form_data = {'phone_number': '09123456789'}
        
        response = self.client.post(reverse('cart'), data=form_data)
        order = Order.objects.last()
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(order.price, Decimal('12.00'))  
        self.assertEqual(order.order_items.count(), 2)

class CheckoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(phone_number="09123456789")
        self.order = Order.objects.create(customer=self.customer, price=10.00)

    def test_checkout_view(self):
        response = self.client.get(reverse('checkout', args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order_id'], self.order.id)

class HistoryViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(phone_number="09123456789")
        self.client.session['customer_id'] = self.customer.id
        self.client.session.save()



    def test_history_view_no_orders(self):
        response = self.client.get(reverse('history'))
        self.assertEqual(response.status_code, 200)
        
      
        orders = response.context.get('orders', None)
        self.assertIsNone(orders)
        
    def test_history_view_no_customer(self):
       
        session = self.client.session
        session.pop('customer_id', None)
        session.save()
        
        response = self.client.get(reverse('history'))
        self.assertEqual(response.status_code, 200)
        
       
        orders = response.context.get('orders', None)
        self.assertIsNone(orders)