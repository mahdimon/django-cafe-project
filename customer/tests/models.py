from django.test import TestCase
from .models import Customer, Order, OrderItem
from core.models import Item  


class CustomerModelTest(TestCase):

    def test_customer_creation_without_phone(self):
        customer = Customer.objects.create()
        self.assertIsNone(customer.phone_number)
        self.assertIsNotNone(customer.created_at)
        self.assertEqual(str(customer), f"Customer {customer.id}")

    def test_customer_creation_with_phone(self):
        customer = Customer.objects.create(phone_number="1234567890")
        self.assertEqual(customer.phone_number, "1234567890")
        self.assertEqual(str(customer), "1234567890")


class OrderModelTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(phone_number="0987654321")
        self.item1 = Item.objects.create(name="Latte", price=4.50, description="Coffee with milk")
        self.item2 = Item.objects.create(name="Espresso", price=3.00, description="Strong coffee")

    def test_order_items_info_on_first_save(self):

        order = Order.objects.create(customer=self.customer, table_number=5, price=7.50)
        order.items.add(self.item1, self.item2)
        

        order.save()
        self.assertIsNotNone(order.items_info) 
        self.assertEqual(len(order.items_info), 2) 


        items_names = [item['name'] for item in order.items_info]
        self.assertIn("Latte", items_names)
        self.assertIn("Espresso", items_names)

    def test_order_items_info_is_unchanged_on_item_update(self):

        order = Order.objects.create(customer=self.customer, table_number=5, price=7.50)
        order.items.add(self.item1, self.item2)
        order.save()
        
        original_items_info = order.items_info.copy()
        self.item1.price = 5.00 
        self.item1.save()
        order.refresh_from_db()
        self.assertEqual(order.items_info, original_items_info)

class OrderItemModelTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(phone_number="0123456789")
        self.order = Order.objects.create(customer=self.customer)
        self.item = Item.objects.create(name="Cappuccino", price=4.00, description="Espresso with milk foam")

    def test_order_item_creation(self):
        order_item = OrderItem.objects.create(order=self.order, item=self.item, quantity=2)
        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.item, self.item)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(str(order_item), "2 of Cappuccino in Order {}".format(self.order.id))
