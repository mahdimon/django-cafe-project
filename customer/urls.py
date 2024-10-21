from django.urls import path
from .views import Menu , Cart
urlpatterns = [
    path('cart/', Cart.as_view(), name='cart'),
    path('', Menu.as_view(), name='menu'),
    
]