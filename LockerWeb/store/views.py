from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Min
from datetime import date
import json

from .models import Locker, Booking, Location
from .forms import SignUpForm, BookingForm

def home(request):
    locations = Location.objects.all()
    search = request.GET.get('search')
    if search:
        locations = locations.filter(Q(name__icontains=search) | Q(city__icontains=search) | Q(zip_code__icontains=search))

    valid_locations = []
    map_data = []

    for loc in locations:
        available_lockers = Locker.objects.filter(location=loc, status='available')
        
        valid_locations.append(loc)
        
        # We build the list here, but we DO NOT convert to JSON string yet
        map_data.append({
            'id': loc.id,
            'name': loc.name,
            'lat': loc.latitude,
            'lng': loc.longitude,
            'address': loc.address,
            'available_count': available_lockers.count(),
        })

    context = {
        'locations': valid_locations,
        'map_data': map_data, # <--- CHANGED: Passed as raw list, not string
        'search_query': search,
    }
    return render(request, 'home.html', context)

def location_detail(request, pk):
    location = get_object_or_404(Location, pk=pk)
    
    available_sizes = (
        Locker.objects
        .filter(location=location, status='available')
        .values('size')
        .annotate(price=Min('daily_price'), count=Count('id'))
        .order_by('size')
    )
    
    size_choices_dict = dict(Locker.SIZE_CHOICES)
    detailed_sizes = []
    for item in available_sizes:
        detailed_sizes.append({
            'code': item['size'],
            'name': size_choices_dict.get(item['size']),
            'price': item['price'],
            'count': item['count']
        })

    context = {
        'location': location,
        'available_sizes': detailed_sizes,
    }
    return render(request, 'location_detail.html', context)

@login_required
def book_cabinet(request, location_id, size):
    location = get_object_or_404(Location, pk=location_id)
    
    locker = Locker.objects.filter(
        location=location, 
        size=size, 
        status='available'
    ).first()
    
    if not locker:
        messages.error(request, "Sorry, there are no longer lockers of that size available at this location.")
        return redirect('location_detail', pk=location_id)
    
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            overlapping = Booking.objects.filter(
                locker=locker,
                status__in=['pending', 'active'],
                start_date__lte=end_date,
                end_date__gte=start_date
            ).exists()
            
            if overlapping:
                messages.error(request, "This specific unit became unavailable. Please try again.")
                return redirect('location_detail', pk=location_id)
            
            booking = form.save(commit=False)
            booking.user = request.user
            booking.locker = locker
            booking.total_price = booking.calculate_total_price()
            booking.save()
            
            if start_date <= date.today():
                locker.status = 'occupied'
                locker.save()
            
            messages.success(request, f"Locker booked successfully! Unit #{locker.locker_number} assigned.")
            return redirect('my_bookings')
    else:
        form = BookingForm()
    
    context = {
        'location': location,
        'locker_size': dict(Locker.SIZE_CHOICES).get(size),
        'price': locker.daily_price,
        'form': form,
    }
    return render(request, 'book_locker.html', context)

# ... (Include login_user, register_user, logout_user, my_bookings, cancel_booking, etc. from previous steps) ...
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return redirect('login')
    else:
        return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "You have registered successfully!")
            return redirect('home')
        else:
            messages.error(request, "Something went wrong. Please try again.")
    return render(request, 'register.html', {"form": form})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    for booking in bookings:
        if booking.status == 'pending' and booking.start_date <= date.today():
            booking.status = 'active'
            booking.save()
        elif booking.status == 'active' and booking.end_date < date.today():
            booking.status = 'completed'
            booking.save()
    
    context = {'bookings': bookings, 'status_filter': status_filter}
    return render(request, 'my_bookings.html', context)

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status not in ['pending', 'active']:
        messages.error(request, "This booking cannot be cancelled.")
        return redirect('my_bookings')
    if request.method == "POST":
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Booking cancelled successfully.")
        return redirect('my_bookings')
    return render(request, 'cancel_booking.html', {'booking': booking})
    
def about(request):
    return render(request, 'about.html', {})
def terms_and_conditions(request):
    return render(request, 'TermsandConditions.htm', {})
def privacy_policy(request):
    return render(request, 'Privacy Policy.htm', {})