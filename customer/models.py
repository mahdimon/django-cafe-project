from django.db import models
from core.models import Item


class Customer(models.Model):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone_number if self.phone_number else f"Customer {self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.name} in Order {self.order.id}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    items = models.ManyToManyField(Item, through='OrderItem', related_name='orders')
    items_info = models.JSONField(null=True, blank=True)
    table_number = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} for Table {self.table_number} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        self.items_info = list(self.items.values('name', 'category', 'description', 'price'))
        super().save(*args, **kwargs)
