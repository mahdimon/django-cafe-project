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
    ItemListView,
    ItemCreateView,
    ItemUpdateView,
    ItemDeleteView,
    category_list,
    CategoryCreateView,  # Ensure this is defined in your views
    CategoryUpdateView,
    CategoryDeleteView,
    OrderListView
)

from django.contrib.auth.views import LogoutView

app_name = 'staff'

urlpatterns = [
    path('', StaffDashboardView.as_view(), name='home'),  # Dashboard home
    path('login/', login_view, name='login'),  # Login view
    path('logout/', views.logout_view, name='logout'),  # Logout view
    path('orders/', OrderListView.as_view(), name='orders'),
    path('orders/<int:pk>/edit/', OrderEditView.as_view(), name='edit_order'),  # Order editing
    path('staff_list/', views.staff_list, name='staff_list'),  # List of staff
    path('create/', views.create_staff, name='create_staff'),  # Create new staff
    path('<int:staff_id>/update/', views.update_staff, name='update_staff'),  # Update staff
    path('<int:staff_id>/delete/', views.delete_staff, name='delete_staff'),  # Delete staff
    path('orders/create/', OrderCreateView.as_view(), name='create_order'),
    path('orders/edit/<int:pk>/', OrderEditView.as_view(), name='order_edit'),
    path('orders/delete/<int:pk>/', OrderDeleteView.as_view(), name='order_delete'),
    path('items/', ItemListView.as_view(), name='item_list'),
    path('items/create/', ItemCreateView.as_view(), name='create_item'),
    path('items/update/<int:pk>/', ItemUpdateView.as_view(), name='update_item'),
    path('items/delete/<int:pk>/', ItemDeleteView.as_view(), name='delete_item'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', CategoryCreateView.as_view(), name='create_category'),  # Update to use class-based view
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='update_category'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_confirm_delete'),



]
