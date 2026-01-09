from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from datetime import date, timedelta

from .models import Locker, Booking, Location
from .forms import SignUpForm, BookingForm


def home(request):
	"""Display available lockers on homepage"""
	lockers = Locker.objects.filter(status='available')
	
	# Filter by location if provided
	location_id = request.GET.get('location')
	if location_id:
		lockers = lockers.filter(location_id=location_id)
	
	# Filter by size if provided
	size = request.GET.get('size')
	if size:
		lockers = lockers.filter(size=size)
	
	# Search by locker number
	search = request.GET.get('search')
	if search:
		lockers = lockers.filter(Q(locker_number__icontains=search) | Q(location__name__icontains=search))
	
	locations = Location.objects.all()
	
	context = {
		'lockers': lockers,
		'locations': locations,
		'selected_location': location_id,
		'selected_size': size,
		'search_query': search,
	}
	return render(request, 'home.html', context)


def about(request):
	"""About page"""
	return render(request, 'about.html', {})


def login_user(request):
	"""User login"""
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
	"""User logout"""
	logout(request)
	messages.success(request, "You have been logged out!")
	return redirect('home')


def register_user(request):
	"""User registration"""
	form = SignUpForm()
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			if user:
				login(request, user)
				messages.success(request, "You have registered successfully!")
				return redirect('home')
		else:
			messages.error(request, "Something went wrong. Please try again.")
	
	return render(request, 'register.html', {"form": form})


def locker_detail(request, pk):
	"""View details of a specific locker"""
	locker = get_object_or_404(Locker, pk=pk)
	
	# Check if locker is available for booking
	is_available = locker.status == 'available'
	
	# Get overlapping bookings to show unavailable dates
	overlapping_bookings = Booking.objects.filter(
		locker=locker,
		status__in=['pending', 'active'],
		end_date__gte=date.today()
	).order_by('start_date')
	
	context = {
		'locker': locker,
		'is_available': is_available,
		'bookings': overlapping_bookings,
	}
	return render(request, 'locker_detail.html', context)


@login_required
def book_locker(request, pk):
	"""Book a locker"""
	locker = get_object_or_404(Locker, pk=pk)
	
	if locker.status != 'available':
		messages.error(request, "This locker is not available for booking.")
		return redirect('locker_detail', pk=pk)
	
	if request.method == "POST":
		form = BookingForm(request.POST)
		if form.is_valid():
			start_date = form.cleaned_data['start_date']
			end_date = form.cleaned_data['end_date']
			
			# Check for overlapping bookings
			overlapping = Booking.objects.filter(
				locker=locker,
				status__in=['pending', 'active'],
				start_date__lte=end_date,
				end_date__gte=start_date
			).exists()
			
			if overlapping:
				messages.error(request, "This locker is already booked for the selected dates. Please choose different dates.")
				return redirect('book_locker', pk=pk)
			
			booking = form.save(commit=False)
			booking.user = request.user
			booking.locker = locker
			booking.total_price = booking.calculate_total_price()
			booking.save()
			
			messages.success(request, f"Locker booked successfully! Total: ${booking.total_price:.2f}")
			return redirect('my_bookings')
	else:
		form = BookingForm()
	
	context = {
		'locker': locker,
		'form': form,
	}
	return render(request, 'book_locker.html', context)


@login_required
def my_bookings(request):
	"""View user's bookings"""
	bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
	
	# Filter by status if provided
	status_filter = request.GET.get('status')
	if status_filter:
		bookings = bookings.filter(status=status_filter)
	
	# Update booking statuses based on dates
	for booking in bookings:
		if booking.status == 'pending' and booking.start_date <= date.today():
			booking.status = 'active'
			booking.save()
		elif booking.status == 'active' and booking.end_date < date.today():
			booking.status = 'completed'
			booking.save()
	
	context = {
		'bookings': bookings,
		'status_filter': status_filter,
	}
	return render(request, 'my_bookings.html', context)


@login_required
def cancel_booking(request, pk):
	"""Cancel a booking"""
	booking = get_object_or_404(Booking, pk=pk, user=request.user)
	
	if booking.status not in ['pending', 'active']:
		messages.error(request, "This booking cannot be cancelled.")
		return redirect('my_bookings')
	
	if request.method == "POST":
		booking.status = 'cancelled'
		booking.save()
		messages.success(request, "Booking cancelled successfully.")
		return redirect('my_bookings')
	
	context = {
		'booking': booking,
	}
	return render(request, 'cancel_booking.html', context)
def terms_and_conditions(request):
	"""Display Terms and Conditions page"""
	return render(request, 'TermsandConditions.htm', {})
def privacy_policy(request):
	"""Display Privacy Policy page"""
	return render(request, 'Privacy Policy.htm', {})
