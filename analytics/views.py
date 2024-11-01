from django.shortcuts import render
from django.views.generic import ListView, FormView,View
from core.models import Item, Category
from customer.models import OrderItem, Order,Customer
from django.db.models import Sum, Q, Count, Value, OuterRef, Subquery, FloatField
from django.db.models.functions import ExtractHour, Coalesce, TruncDay, TruncMonth, TruncYear, Cast
from .forms import SalesReportForm, PopularItemsForm , DateSelectionForm
from django.utils import timezone
from datetime import datetime , date

def index(request):
    context = {}
    return render(request, 'analytics/index.html', context)

class PopularItemsView(View):
    template_name = 'analytics/popular_items.html'

    def get(self, request):
        form = PopularItemsForm()
        popular_items = Item.objects.annotate(
            total_sold=Coalesce(
                Sum('order_items__quantity', filter=Q(order_items__order__status='completed')),
                Value(0)
            )
        ).order_by('-total_sold')[:5]
        return render(request, self.template_name, {'form': form, 'popular_items': popular_items})

   
    def post(self, request):
        form = PopularItemsForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            # Check if start_date and end_date are date instances and convert them to datetime
            if start_date and isinstance(start_date, (date, datetime)):
                start_date = datetime.combine(start_date, datetime.min.time())
            if end_date and isinstance(end_date, (date, datetime)):
                end_date = datetime.combine(end_date, datetime.max.time())

            # Make datetimes timezone-aware
            if start_date and timezone.is_naive(start_date):
                start_date = timezone.make_aware(start_date)
            if end_date and timezone.is_naive(end_date):
                end_date = timezone.make_aware(end_date)

            popular_items = Item.objects.annotate(
                total_sold=Coalesce(
                    Sum('order_items__quantity', filter=Q(order_items__order__status='completed') & 
                                                Q(order_items__order__order_date__range=(start_date, end_date)) if start_date and end_date else 
                                                Q(order_items__order__status='completed')),
                    Value(0)
                )
            ).order_by('-total_sold')[:5]

        return render(request, self.template_name, {'form': form, 'popular_items': popular_items})

class PeakHoursView(ListView):
    template_name = 'analytics/peak_hours.html'
    context_object_name = 'peak_hours'

    def get_queryset(self):

        peak_hours = Order.objects.annotate(
            hour=ExtractHour('order_date')
        ).values('hour').annotate(
            order_count=Count('id')
        ).order_by('-order_count')[:5]
        return peak_hours


class CustomerDemographicsView(ListView):
    template_name = 'analytics/customer_demographics.html'
    context_object_name = 'top_tables'

    def get_queryset(self):
        top_tables = Order.objects.values('table_number').annotate(
            order_count=Count('id')
        ).order_by('-order_count')[:5]
        return top_tables




class SalesReportView(FormView):
    template_name = 'analytics/sales_report.html'
    form_class = SalesReportForm

    def form_valid(self, form):
        category = form.cleaned_data.get('category')
        customer = form.cleaned_data.get('customer')
        time_of_day = form.cleaned_data.get('time_of_day')
        time_frame = form.cleaned_data.get('time_frame')

        queryset = Order.objects.all()
        if category:
            queryset = queryset.filter(items__category=category)
        if customer:
            queryset = queryset.filter(customer=customer)
        if time_of_day:
            queryset = queryset.filter(order_date__hour=time_of_day)

        if time_frame == 'total':
            sales_data = queryset.aggregate(total_sales=Sum('price'))
            sales_data = [{'total_sales': sales_data['total_sales']}]
            
           
        elif time_frame == 'monthly':
            sales_data = (
                queryset
                .annotate(month=TruncMonth('order_date')) 
                .values('month')  
                .annotate(total_sales=Sum('price'))
                .order_by('month')  
            )
        elif time_frame == 'daily':
            sales_data = (
                queryset
                .annotate(day=TruncDay('order_date')) 
                .values('day') 
                .annotate(total_sales=Sum('price')) 
                .order_by('day')
            )
        elif time_frame == 'yearly':
            sales_data = (
                queryset
                .annotate(year=TruncYear('order_date')) 
                .values('year')  
                .annotate(total_sales=Sum('price')) 
                .order_by('year') 
            )

      
        context = self.get_context_data(form=form, sales_data=sales_data, time_frame=time_frame)
        return self.render_to_response(context)
        
class OrderStatusesByDateView(View):
    template_name = 'analytics/today_orders.html'

    def get(self, request):
        # Default to today's date if no date is selected
        form = DateSelectionForm()
        selected_date = timezone.now().date()
        order_statuses = self.get_order_statuses(selected_date)
        return render(request, self.template_name, {'form': form, 'order_statuses': order_statuses})

    def post(self, request):

        form = DateSelectionForm(request.POST)
        if form.is_valid():
            selected_date = form.cleaned_data['selected_date']
            order_statuses = self.get_order_statuses(selected_date)
        else:
            selected_date = timezone.now().date()
            order_statuses = self.get_order_statuses(selected_date)
        return render(request, self.template_name, {'form': form, 'order_statuses': order_statuses})

    def get_order_statuses(self, selected_date):
        return Order.objects.filter(order_date__date=selected_date).values('status').annotate(count=Count('id'))
    
class CustomerOrderHistoryView(ListView):
    template_name = 'analytics/customer_order_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        phone_number = self.request.GET.get('phone_number')
        if phone_number:
            customer = Customer.objects.filter(phone_number=phone_number).first()
            if customer:
                return Order.objects.filter(customer=customer).order_by("-order_date")
        return []