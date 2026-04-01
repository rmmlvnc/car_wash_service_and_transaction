from django.urls import path
from . import views

urlpatterns = [
    # Admin dashboard
    path('', views.main, name='main'),

    # Customers
    path('customer/', views.customer_list, name='customer_list'),
    path('customer/add/', views.add_customer, name='add_customer'),
    path('customer/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customer/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customer/<int:pk>/delete/', views.customer_delete, name='customer_delete'),

    # Cars
    path('customer/<int:customer_pk>/car/add/', views.car_add, name='car_add'),
    path('car/<int:pk>/edit/', views.car_edit, name='car_edit'),
    path('car/<int:pk>/delete/', views.car_delete, name='car_delete'),

    # Services
    path('service/', views.service_list, name='service_list'),
    path('service/new/', views.service_new, name='service_new'),
    path('service/<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('service/<int:pk>/delete/', views.service_delete, name='service_delete'),

    # Transactions
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/new/', views.transaction_new, name='transaction_new'),
    path('transactions/<int:pk>/', views.transaction_detail, name='transaction_detail'),
    path('transactions/<int:pk>/status/', views.transaction_update_status, name='transaction_update_status'),

    # Payments
    path('transactions/<int:tx_pk>/pay/', views.payment_create, name='payment_create'),
    path('transactions/<int:tx_pk>/paypal/', views.paypal_create_order, name='paypal_create_order'),
    path('transactions/<int:tx_pk>/paypal/capture/', views.paypal_capture, name='paypal_capture'),

    # Customer Portal
    path('portal/', views.portal_home, name='portal_home'),
    path('portal/register/', views.portal_register, name='portal_register'),
    path('portal/login/', views.portal_login, name='portal_login'),
    path('portal/logout/', views.portal_logout, name='portal_logout'),
    path('portal/book/', views.portal_book, name='portal_book'),
    path('portal/pay/<int:tx_pk>/', views.portal_pay, name='portal_pay'),
    path('portal/car/add/', views.portal_add_car, name='portal_add_car'),
    path('portal/cars/', views.portal_cars, name='portal_cars'),
    path('portal/profile/', views.portal_profile, name='portal_profile'),
    path('portal/transactions/', views.portal_transactions, name='portal_transactions'),
    path('portal/transactions/<int:tx_pk>/cancel/', views.portal_cancel_transaction, name='portal_cancel_transaction'),
]