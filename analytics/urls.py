from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.index, name='index'),
    path('popular_items/', views.PopularItemsView.as_view(), name='popular_items'),
    path('peak_hours/', views.PeakHoursView.as_view(), name='peak_hours'),
    path('customer_demographics/', views.CustomerDemographicsView.as_view(), name='customer_demographics'),
    path('sales/', views.SalesReportView.as_view(), name='sales'),
#     path('download_sales_reports/', views.download_sales_reports, name='download_sales_reports'),

    path('order_status_report/', views.OrderStatusesByDateView.as_view(), name='order_status_report'),
#     path('sales_by_employee_report/', views.sales_by_employee_report, name='sales_by_employee_report'),
    path('customer_order_history_report/', views.CustomerOrderHistoryView.as_view(), name='customer_order_history_report'),
    path('sales-report/csv/', views.SalesReportCSVView.as_view(), name='sales_report_csv'),
 ]