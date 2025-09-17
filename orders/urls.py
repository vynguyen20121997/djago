from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<uuid:order_id>/', views.payment_instructions, name='payment_instructions'),
    path('<uuid:order_id>/', views.order_detail, name='order_detail'),
]