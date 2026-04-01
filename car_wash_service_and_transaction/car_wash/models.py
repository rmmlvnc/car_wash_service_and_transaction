from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user           = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name     = models.CharField(max_length=100)
    middle_name    = models.CharField(max_length=100, blank=True)
    last_name      = models.CharField(max_length=100)
    address        = models.CharField(max_length=255, blank=True)
    contact_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['last_name', 'first_name']


class Car(models.Model):
    CAR_TYPE_CHOICES = [
        ('sedan',      'Sedan'),
        ('suv',        'SUV'),
        ('van',        'Van'),
        ('pickup',     'Pickup Truck'),
        ('hatchback',  'Hatchback'),
        ('coupe',      'Coupe'),
        ('motorcycle', 'Motorcycle'),
        ('other',      'Other'),
    ]

    customer     = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cars')
    plate_number = models.CharField(max_length=20)
    make         = models.CharField(max_length=100, help_text="e.g. Toyota")
    model_name   = models.CharField(max_length=100, help_text="e.g. Vios")
    year         = models.PositiveIntegerField(null=True, blank=True)
    color        = models.CharField(max_length=50, blank=True)
    car_type     = models.CharField(max_length=20, choices=CAR_TYPE_CHOICES, default='sedan')

    def __str__(self):
        return f"{self.plate_number} — {self.year or ''} {self.make} {self.model_name}"

    class Meta:
        ordering = ['plate_number']


class Service(models.Model):
    service_type     = models.CharField(max_length=100)
    service_name     = models.CharField(max_length=100)
    description      = models.TextField(blank=True)
    price            = models.DecimalField(max_digits=8, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=30, help_text="Estimated duration in minutes")
    is_package       = models.BooleanField(default=False, help_text="Mark as a package deal")

    def __str__(self):
        return f"{self.service_name} ({self.service_type})"

    class Meta:
        ordering = ['service_type', 'service_name']


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('in_progress', 'In Progress'),
        ('completed',   'Completed'),
        ('cancelled',   'Cancelled'),
    ]

    customer         = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='transactions')
    car              = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    service          = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='transactions')
    transaction_date = models.DateTimeField(auto_now_add=True)
    scheduled_date   = models.DateField(null=True, blank=True, help_text="Customer's preferred service date")
    scheduled_time   = models.TimeField(null=True, blank=True, help_text="Customer's preferred service time")
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes            = models.TextField(blank=True)

    def __str__(self):
        return f"#{self.pk} — {self.customer} | {self.service.service_name}"

    @property
    def amount(self):
        return self.service.price

    class Meta:
        ordering = ['-transaction_date']


class Payment(models.Model):
    METHOD_CHOICES = [
        ('paypal', 'PayPal'),
        ('cash',   'Cash'),
    ]
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('completed', 'Completed'),
        ('failed',    'Failed'),
        ('refunded',  'Refunded'),
    ]

    transaction     = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='payment')
    amount          = models.DecimalField(max_digits=8, decimal_places=2)
    payment_date    = models.DateTimeField(auto_now_add=True)
    payment_method  = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash')
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paypal_order_id = models.CharField(max_length=100, blank=True, null=True)
    paypal_payer_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Payment #{self.pk} — {self.get_status_display()}"