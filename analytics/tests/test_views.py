from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import date
from core.models import Item
from customer.models import Order, OrderItem, Customer


class PopularItemsViewTest(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user(
            username="staffuser", password="password")
        self.user.is_staff = True
        self.user.save()
        self.client.login(username="staffuser", password="password")

       
        self.url = reverse('analytics:popular_items')
        self.item1 = Item.objects.create(
            name="Item 1", price=10.00, available=True)
        self.item2 = Item.objects.create(
            name="Item 2", price=20.00, available=True)
        self.customer = Customer.objects.create(phone_number="123456789")
        self.order1 = Order.objects.create(customer=self.customer, price=30.00)
        OrderItem.objects.create(
            order=self.order1, item=self.item1, quantity=2)
        OrderItem.objects.create(
            order=self.order1, item=self.item2, quantity=1)

    def test_popular_items_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/popular_items.html')
        self.assertIn(self.item1, response.context['popular_items'])
        self.assertIn(self.item2, response.context['popular_items'])

    def test_popular_items_post(self):
        form_data = {'start_date': date.today(), 'end_date': date.today()}
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.item1, response.context['popular_items'])
        self.assertIn(self.item2, response.context['popular_items'])


class PeakHoursViewTest(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user(
            username="staffuser", password="password")
        self.user.is_staff = True
        self.user.save()
        self.client.login(username="staffuser", password="password")

       
        self.url = reverse('analytics:peak_hours')
        self.customer = Customer.objects.create(phone_number="123456789")
        self.order1 = Order.objects.create(
            customer=self.customer, price=30.00, order_date=timezone.now())
        self.order2 = Order.objects.create(
            customer=self.customer, price=50.00, order_date=timezone.now())

    def test_peak_hours_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/peak_hours.html')
        self.assertIn('peak_hours', response.context)


class CustomerDemographicsViewTest(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user(
            username="staffuser", password="password")
        self.user.is_staff = True
        self.user.save()
        self.client.login(username="staffuser", password="password")

        
        self.url = reverse('analytics:customer_demographics')
        self.customer = Customer.objects.create(phone_number="123456789")
        self.order1 = Order.objects.create(
            customer=self.customer, price=30.00, table_number=1)
        self.order2 = Order.objects.create(
            customer=self.customer, price=50.00, table_number=2)

    def test_customer_demographics_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'analytics/customer_demographics.html')
        self.assertIn('top_tables', response.context)


class OrderStatusesByDateViewTest(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user(
            username="staffuser", password="password")
        self.user.is_staff = True
        self.user.save()
        self.client.login(username="staffuser", password="password")

        
        self.url = reverse('analytics:order_status_report')
        self.customer = Customer.objects.create(phone_number="123456789")
        self.order1 = Order.objects.create(
            customer=self.customer, price=30.00, order_date=timezone.now(), status='completed')
        self.order2 = Order.objects.create(
            customer=self.customer, price=50.00, order_date=timezone.now(), status='pending')

    def test_order_statuses_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/today_orders.html')
        self.assertIn('order_statuses', response.context)

    def test_order_statuses_post(self):
        form_data = {'selected_date': timezone.now().date()}
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 200)


class CustomerOrderHistoryViewTest(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user(
            username="staffuser", password="password")
        self.user.is_staff = True
        self.user.save()
        self.client.login(username="staffuser", password="password")

        
        self.url = reverse('analytics:customer_order_history_report')
        self.customer = Customer.objects.create(phone_number="123456789")
        self.order1 = Order.objects.create(
            customer=self.customer, price=30.00, order_date=timezone.now())
        self.order2 = Order.objects.create(
            customer=self.customer, price=50.00, order_date=timezone.now())

    def test_customer_order_history_get(self):
        response = self.client.get(
            self.url, {'phone_number': self.customer.phone_number})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'analytics/customer_order_history.html')
        self.assertIn(self.order1, response.context['orders'])
        self.assertIn(self.order2, response.context['orders'])
