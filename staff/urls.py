from django.urls import path
from . import views
from .views import home, login_view
from django.contrib.auth.views import LogoutView

app_name = 'staff'

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('orders/', views.orders_view, name='orders'),
    path('staff_list', views.staff_list, name='staff_list'),
    path('logout/', views.logout_view, name='logout'),
    path('create/', views.create_staff, name='create_staff'),
    path('<int:staff_id>/update/', views.update_staff, name='update_staff'),
    path('<int:staff_id>/delete/', views.delete_staff, name='delete_staff'),
]   