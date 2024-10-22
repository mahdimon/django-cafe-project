from django.urls import path
from . import views
from .views import (
    staff_list,
    create_staff,
    update_staff,
    delete_staff,
    login_view,
    StaffDashboardView,
    orders_view,
    logout_view,
    OrderEditView,
    OrderCreateView,
    OrderDeleteView,
    OrderUpdateView
)

from django.contrib.auth.views import LogoutView

app_name = 'staff'

urlpatterns = [
    path('', StaffDashboardView.as_view(), name='home'),  # Dashboard home
    path('login/', login_view, name='login'),  # Login view
    path('logout/', views.logout_view, name='logout'),  # Logout view
    path('orders/', orders_view, name='orders'),
    path('orders/<int:pk>/edit/', OrderEditView.as_view(), name='edit_order'),  # Order editing
    path('staff_list/', views.staff_list, name='staff_list'),  # List of staff
    path('create/', views.create_staff, name='create_staff'),  # Create new staff
    path('<int:staff_id>/update/', views.update_staff, name='update_staff'),  # Update staff
    path('<int:staff_id>/delete/', views.delete_staff, name='delete_staff'),  # Delete staff
    path('orders/create/', OrderCreateView.as_view(), name='create_order'),
    path('orders/edit/<int:pk>/', OrderUpdateView.as_view(), name='order_edit'),
    path('orders/delete/<int:pk>/', OrderDeleteView.as_view(), name='order_delete'),
]
