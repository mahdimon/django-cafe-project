from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)  # e.g., "Appetizers", "Drinks"
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Item(models.Model):
    category = models.ForeignKey(Category, null=True , on_delete=models.SET_NULL,related_name='items')
    name = models.CharField(max_length=100)  
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)  
    available = models.BooleanField(default=True)  

    def __str__(self):
        return self.name
