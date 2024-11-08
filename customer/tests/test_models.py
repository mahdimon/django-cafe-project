from django.test import TestCase
from customer.models import Customer, Order, OrderItem
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
