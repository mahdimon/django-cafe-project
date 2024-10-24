from django.urls import path
from .views import Menu , Cart , checkout,history
urlpatterns = [
    path('cart/', Cart.as_view(), name='cart'),
    path('', Menu.as_view(), name='menu'),
    path('checkout', checkout, name='checkout'),
    path('history', checkout, name='history'),
    
]