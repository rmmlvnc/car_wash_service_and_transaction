from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from .models import Customer, Car, Service, Transaction, Payment

# ─── ADMIN DASHBOARD ──────────────────────────────────────────────────────────
def main(request):
    context = {
        'total_customers':    Customer.objects.count(),
        'total_services':     Service.objects.count(),
        'total_transactions': Transaction.objects.count(),
        'total_revenue':      sum(p.amount for p in Payment.objects.filter(status='completed')),
        'recent_transactions': Transaction.objects.select_related('customer', 'service', 'car')[:5],
        'pending_payments':   Payment.objects.filter(status='pending').count(),
    }
    return render(request, 'main.html', context)


# ─── CUSTOMERS ────────────────────────────────────────────────────────────────
def customer_list(request):
    customers = Customer.objects.prefetch_related('cars', 'transactions').all()
    return render(request, 'customers_list.html', {'customer_list': customers})


def add_customer(request):
    if request.method == 'POST':
        first_name     = request.POST.get('first_name', '').strip()
        middle_name    = request.POST.get('middle_name', '').strip()
        last_name      = request.POST.get('last_name', '').strip()
        address        = request.POST.get('address', '').strip()
        contact_number = request.POST.get('contact_number', '').strip()

        if not first_name or not last_name:
            messages.error(request, 'First name and last name are required.')
            return render(request, 'add_customer.html', {'post': request.POST})

        Customer.objects.create(
            first_name=first_name, middle_name=middle_name,
            last_name=last_name, address=address, contact_number=contact_number,
        )
        messages.success(request, f'Customer {first_name} {last_name} added.')
        return redirect('customer_list')

    return render(request, 'add_customer.html')


def customer_detail(request, pk):
    c = get_object_or_404(Customer, pk=pk)
    cars = c.cars.all()
    transactions = c.transactions.select_related('service', 'car').prefetch_related('payment').all()
    return render(request, 'customer_details.html', {
        'customer': c, 'cars': cars, 'transactions': transactions
    })


def customer_edit(request, pk):
    c = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        c.first_name     = request.POST.get('first_name', c.first_name).strip()
        c.middle_name    = request.POST.get('middle_name', c.middle_name).strip()
        c.last_name      = request.POST.get('last_name', c.last_name).strip()
        c.address        = request.POST.get('address', c.address).strip()
        c.contact_number = request.POST.get('contact_number', c.contact_number).strip()
        c.save()
        messages.success(request, 'Customer updated.')
        return redirect('customer_detail', pk=pk)
    return render(request, 'customer_edit.html', {'customer': c})


def customer_delete(request, pk):
    c = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        c.delete()
        messages.success(request, 'Customer deleted.')
        return redirect('customer_list')
    return render(request, 'customer_confirm_delete.html', {'customer': c})


# ─── CARS ─────────────────────────────────────────────────────────────────────
def car_add(request, customer_pk):
    customer = get_object_or_404(Customer, pk=customer_pk)
    if request.method == 'POST':
        Car.objects.create(
            customer=customer,
            plate_number=request.POST.get('plate_number', '').strip().upper(),
            make=request.POST.get('make', '').strip(),
            model_name=request.POST.get('model_name', '').strip(),
            year=request.POST.get('year') or None,
            color=request.POST.get('color', '').strip(),
            car_type=request.POST.get('car_type', 'sedan'),
        )
        messages.success(request, 'Car added.')
        return redirect('customer_detail', pk=customer_pk)
    return render(request, 'car_add.html', {'customer': customer, 'car_types': Car.CAR_TYPE_CHOICES})


def car_edit(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        car.plate_number = request.POST.get('plate_number', car.plate_number).strip().upper()
        car.make         = request.POST.get('make', car.make).strip()
        car.model_name   = request.POST.get('model_name', car.model_name).strip()
        car.year         = request.POST.get('year') or None
        car.color        = request.POST.get('color', car.color).strip()
        car.car_type     = request.POST.get('car_type', car.car_type)
        car.save()
        messages.success(request, 'Car updated.')
        return redirect('customer_detail', pk=car.customer_id)
    return render(request, 'car_edit.html', {'car': car, 'car_types': Car.CAR_TYPE_CHOICES})


def car_delete(request, pk):
    car = get_object_or_404(Car, pk=pk)
    customer_pk = car.customer_id
    if request.method == 'POST':
        car.delete()
        messages.success(request, 'Car removed.')
        return redirect('customer_detail', pk=customer_pk)
    return render(request, 'car_confirm_delete.html', {'car': car})


# ─── SERVICES ─────────────────────────────────────────────────────────────────
def service_list(request):
    services = Service.objects.all()
    return render(request, 'service_list.html', {'service_list': services})


def service_new(request):
    if request.method == 'POST':
        name     = request.POST.get('service_name', '').strip()
        stype    = request.POST.get('service_type', '').strip()
        desc     = request.POST.get('description', '').strip()
        price    = request.POST.get('price', '').strip()
        duration = request.POST.get('duration_minutes', '30').strip()

        if not name or not stype or not price:
            messages.error(request, 'Service name, type and price are required.')
            return render(request, 'service_new.html', {'post': request.POST})

        try:
            price = float(price)
            duration = int(duration)
        except ValueError:
            messages.error(request, 'Invalid price or duration.')
            return render(request, 'service_new.html', {'post': request.POST})

        is_package = request.POST.get('is_package') == 'on'
        Service.objects.create(service_name=name, service_type=stype, description=desc,
                               price=price, duration_minutes=duration, is_package=is_package)
        messages.success(request, f'Service "{name}" created.')
        return redirect('service_list')

    return render(request, 'service_new.html')


def service_edit(request, pk):
    svc = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        svc.service_name     = request.POST.get('service_name', svc.service_name).strip()
        svc.service_type     = request.POST.get('service_type', svc.service_type).strip()
        svc.description      = request.POST.get('description', svc.description).strip()
        svc.duration_minutes = int(request.POST.get('duration_minutes', svc.duration_minutes))
        svc.is_package        = request.POST.get('is_package') == 'on'
        try:
            svc.price = float(request.POST.get('price', svc.price))
        except ValueError:
            messages.error(request, 'Invalid price.')
            return render(request, 'service_edit.html', {'service': svc})
        svc.save()
        messages.success(request, f'Service "{svc.service_name}" updated.')
        return redirect('service_list')
    return render(request, 'service_edit.html', {'service': svc})


def service_delete(request, pk):
    svc = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        svc.delete()
        messages.success(request, 'Service deleted.')
        return redirect('service_list')
    return render(request, 'service_confirm_delete.html', {'service': svc})


# ─── TRANSACTIONS ─────────────────────────────────────────────────────────────
def transaction_list(request):
    txs = Transaction.objects.select_related('customer', 'service', 'car').prefetch_related('payment').all()
    return render(request, 'transaction_list.html', {'transactions': txs})


def transaction_new(request):
    customers = Customer.objects.prefetch_related('cars').all()
    services  = Service.objects.all()

    if request.method == 'POST':
        customer_id = request.POST.get('customer', '').strip()
        service_id  = request.POST.get('service', '').strip()
        car_id      = request.POST.get('car', '').strip()
        notes       = request.POST.get('notes', '').strip()

        if not customer_id or not service_id:
            messages.error(request, 'Customer and service are required.')
            return render(request, 'transaction_new.html', {'customers': customers, 'services': services, 'post': request.POST})

        c   = get_object_or_404(Customer, pk=customer_id)
        s   = get_object_or_404(Service, pk=service_id)
        car = Car.objects.filter(pk=car_id).first() if car_id else None

        tx = Transaction.objects.create(customer=c, service=s, car=car, notes=notes)
        messages.success(request, 'Transaction created.')
        return redirect('transaction_detail', pk=tx.pk)

    return render(request, 'transaction_new.html', {'customers': customers, 'services': services})


def transaction_detail(request, pk):
    tx = get_object_or_404(Transaction.objects.select_related('customer', 'service', 'car').prefetch_related('payment'), pk=pk)
    return render(request, 'transaction_detail.html', {'transaction': tx})


def transaction_update_status(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Transaction.STATUS_CHOICES):
            tx.status = status
            tx.save()
            messages.success(request, 'Status updated.')
    return redirect('transaction_detail', pk=pk)


# ─── PAYMENTS ─────────────────────────────────────────────────────────────────
def payment_create(request, tx_pk):
    tx = get_object_or_404(Transaction, pk=tx_pk)
    if hasattr(tx, 'payment'):
        messages.info(request, 'Payment already exists for this transaction.')
        return redirect('transaction_detail', pk=tx_pk)
    if request.method == 'POST':
        method = request.POST.get('payment_method', 'cash')
        Payment.objects.create(transaction=tx, amount=tx.amount, payment_method=method)
        if method == 'cash':
            tx.status = 'completed'
            tx.save()
            messages.success(request, 'Cash payment recorded.')
            return redirect('transaction_detail', pk=tx_pk)
        return redirect('paypal_create_order', tx_pk=tx_pk)
    return render(request, 'payment_create.html', {'transaction': tx})


# ─── PAYPAL SANDBOX ───────────────────────────────────────────────────────────
from django.conf import settings as django_settings
PAYPAL_CLIENT_ID = getattr(django_settings, 'PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = ''
PAYPAL_BASE_URL      = 'https://api-m.sandbox.paypal.com'


def paypal_create_order(request, tx_pk):
    tx = get_object_or_404(Transaction, pk=tx_pk)
    return render(request, 'paypal_checkout.html', {
        'transaction': tx,
        'paypal_client_id': PAYPAL_CLIENT_ID,
    })


@csrf_exempt
def paypal_capture(request, tx_pk):
    tx = get_object_or_404(Transaction, pk=tx_pk)
    if request.method == 'POST':
        order_id = request.POST.get('orderID', '')
        payer_id = request.POST.get('payerID', '')

        payment, created = Payment.objects.get_or_create(
            transaction=tx,
            defaults={'amount': tx.amount, 'payment_method': 'paypal'}
        )
        payment.paypal_order_id = order_id
        payment.paypal_payer_id = payer_id
        payment.status          = 'completed'
        payment.save()

        tx.status = 'completed'
        tx.save()

        return HttpResponse('ok', status=200)
    return HttpResponse('invalid', status=400)


# ─── CUSTOMER PORTAL ──────────────────────────────────────────────────────────
def portal_register(request):
    if request.user.is_authenticated:
        return redirect('portal_home')

    if request.method == 'POST':
        first_name     = request.POST.get('first_name', '').strip()
        middle_name    = request.POST.get('middle_name', '').strip()
        last_name      = request.POST.get('last_name', '').strip()
        address        = request.POST.get('address', '').strip()
        contact_number = request.POST.get('contact_number', '').strip()
        username       = request.POST.get('username', '').strip()
        password       = request.POST.get('password', '')
        password2      = request.POST.get('password2', '')

        if not first_name or not last_name or not username or not password:
            messages.error(request, 'All required fields must be filled.')
            return render(request, 'customer_register.html', {'post': request.POST})

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'customer_register.html', {'post': request.POST})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'customer_register.html', {'post': request.POST})

        user = User.objects.create_user(username=username, password=password)
        Customer.objects.create(user=user, first_name=first_name, middle_name=middle_name,
                                last_name=last_name, address=address, contact_number=contact_number)
        login(request, user)
        messages.success(request, f'Welcome, {first_name}!')
        return redirect('portal_home')

    return render(request, 'customer_register.html')


def portal_login(request):
    if request.user.is_authenticated:
        return redirect('portal_home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user     = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('portal_home')
        messages.error(request, 'Invalid username or password.')
        return render(request, 'customer_login.html', {'post': request.POST})

    return render(request, 'customer_login.html')


def portal_logout(request):
    logout(request)
    return redirect('portal_login')


@login_required(login_url='/portal/login/')
def portal_home(request):
    try:
        c = request.user.customer
    except Customer.DoesNotExist:
        logout(request)
        messages.error(request, 'No customer profile found. Please register.')
        return redirect('portal_register')

    services         = Service.objects.filter(is_package=False)
    package_services = Service.objects.filter(is_package=True)
    transactions     = c.transactions.select_related('service', 'car').prefetch_related('payment').all()
    cars             = c.cars.all()
    return render(request, 'customer_home.html', {
        'customer':         c,
        'services':         services,
        'package_services': package_services,
        'transactions':     transactions,
        'cars':             cars,
    })


@login_required(login_url='/portal/login/')
def portal_book(request):
    try:
        c = request.user.customer
    except Customer.DoesNotExist:
        logout(request)
        messages.error(request, 'No customer profile found. Please register.')
        return redirect('portal_register')

    services         = Service.objects.filter(is_package=False)
    package_services = Service.objects.filter(is_package=True)
    cars             = c.cars.all()

    if request.method == 'POST':
        service_id = request.POST.get('service', '').strip()
        car_id         = request.POST.get('car', '').strip()
        notes          = request.POST.get('notes', '').strip()
        scheduled_date = request.POST.get('scheduled_date', '').strip() or None
        scheduled_time = request.POST.get('scheduled_time', '').strip() or None

        if not service_id:
            messages.error(request, 'Please select a service.')
            return render(request, 'customer_book.html', {'services': services, 'package_services': package_services, 'cars': cars, 'post': request.POST, 'today': date.today().isoformat()})

        # Block Sunday bookings
        if scheduled_date:
            from datetime import datetime
            try:
                day = datetime.strptime(scheduled_date, '%Y-%m-%d').weekday()  # 6 = Sunday
                if day == 6:
                    messages.error(request, 'We are closed on Sundays. Please choose another day.')
                    return render(request, 'customer_book.html', {'services': services, 'package_services': package_services, 'cars': cars, 'post': request.POST, 'today': date.today().isoformat()})
            except ValueError:
                pass

        s   = get_object_or_404(Service, pk=service_id)
        car = Car.objects.filter(pk=car_id, customer=c).first() if car_id else None
        tx  = Transaction.objects.create(
            customer=c, service=s, car=car, notes=notes,
            scheduled_date=scheduled_date, scheduled_time=scheduled_time,
        )
        messages.success(request, 'Booking submitted! Proceed to payment.')
        return redirect('portal_pay', tx_pk=tx.pk)

    preselected = request.GET.get('service', '')
    return render(request, 'customer_book.html', {
        'services':         services,
        'package_services': package_services,
        'cars':             cars,
        'today':            date.today().isoformat(),
        'preselected':      preselected,
    })


@login_required(login_url='/portal/login/')
def portal_pay(request, tx_pk):
    try:
        c = request.user.customer
    except Customer.DoesNotExist:
        logout(request)
        messages.error(request, 'No customer profile found. Please register.')
        return redirect('portal_register')

    tx = get_object_or_404(Transaction, pk=tx_pk, customer=c)
    return render(request, 'customer_pay.html', {
        'transaction': tx,
        'paypal_client_id': PAYPAL_CLIENT_ID,
    })


@login_required(login_url='/portal/login/')
def portal_add_car(request):
    try:
        c = request.user.customer
    except Customer.DoesNotExist:
        logout(request)
        messages.error(request, 'No customer profile found. Please register.')
        return redirect('portal_register')

    if request.method == 'POST':
        Car.objects.create(
            customer=c,
            plate_number=request.POST.get('plate_number', '').strip().upper(),
            make=request.POST.get('make', '').strip(),
            model_name=request.POST.get('model_name', '').strip(),
            year=request.POST.get('year') or None,
            color=request.POST.get('color', '').strip(),
            car_type=request.POST.get('car_type', 'sedan'),
        )
        messages.success(request, 'Car added.')
        return redirect('portal_cars')

    return render(request, 'customer_add_car.html', {'car_types': Car.CAR_TYPE_CHOICES})


@login_required(login_url='/portal/login/')
def portal_profile(request):
    try:
        c = request.user.customer
    except Customer.DoesNotExist:
        logout(request)
        return redirect('portal_register')

    if request.method == 'POST':
        c.first_name     = request.POST.get('first_name', c.first_name).strip()
        c.middle_name    = request.POST.get('middle_name', c.middle_name).strip()
        c.last_name      = request.POST.get('last_name', c.last_name).strip()
        c.contact_number = request.POST.get('contact_number', c.contact_number).strip()
        c.address        = request.POST.get('address', c.address).strip()
        c.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('portal_profile')

    all_txs             = c.transactions.select_related('service', 'car').prefetch_related('payment').all()
    active_transactions = all_txs.filter(status__in=['pending', 'in_progress'])
    past_transactions   = all_txs.filter(status__in=['completed', 'cancelled'])
    cars                = c.cars.all()

    return render(request, 'customer_profile.html', {
        'customer':            c,
        'cars':                cars,
        'active_transactions': active_transactions,
        'past_transactions':   past_transactions,
    })


@login_required(login_url='/portal/login/')
def portal_transactions(request):
    try:
        c = request.user.customer
    except Customer.DoesNotExist:
        logout(request)
        return redirect('portal_register')

    all_txs             = c.transactions.select_related('service', 'car').prefetch_related('payment').all()
    active_transactions = all_txs.filter(status__in=['pending', 'in_progress'])
    past_transactions   = all_txs.filter(status__in=['completed', 'cancelled'])

    return render(request, 'customer_transactions.html', {
        'active_transactions': active_transactions,
        'past_transactions':   past_transactions,
    })


@login_required(login_url='/portal/login/')
def portal_cancel_transaction(request, tx_pk):
    try:
        c = request.user.customer
    except Customer.DoesNotExist:
        logout(request)
        return redirect('portal_register')

    tx = get_object_or_404(Transaction, pk=tx_pk, customer=c)
    if request.method == 'POST' and tx.status == 'pending':
        tx.status = 'cancelled'
        tx.save()
        messages.success(request, f'Transaction #{tx.pk} has been cancelled.')
    return redirect('portal_profile')

@login_required(login_url='/portal/login/')
def portal_cars(request):
    try:
        c = request.user.customer
    except Customer.DoesNotExist:
        logout(request)
        messages.error(request, 'No customer profile found. Please register.')
        return redirect('portal_register')

    cars = c.cars.prefetch_related('transactions__service').all()
    return render(request, 'customer_cars.html', {'cars': cars})
