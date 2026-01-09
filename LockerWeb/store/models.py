from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import datetime

class Category(models.Model):
	name = models.CharField(max_length=50)

	def __str__(self):
		return self.name


class Customer(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	phone = models.CharField(max_length=15)
	email = models.EmailField(max_length=100)

	def __str__(self):
		return f'{self.first_name} {self.last_name}'


class Location(models.Model):
	name = models.CharField(max_length=100)
	address = models.TextField()
	description = models.TextField(blank=True)

	def __str__(self):
		return self.name


class Locker(models.Model):
	SIZE_CHOICES = [
		('small', 'Small (12" x 12" x 12")'),
		('medium', 'Medium (18" x 18" x 18")'),
		('large', 'Large (24" x 24" x 24")'),
		('xlarge', 'Extra Large (30" x 30" x 30")'),
	]

	STATUS_CHOICES = [
		('available', 'Available'),
		('occupied', 'Occupied'),
		('maintenance', 'Under Maintenance'),
	]

	locker_number = models.CharField(max_length=20, unique=True)
	location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='lockers')
	size = models.CharField(max_length=20, choices=SIZE_CHOICES)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
	daily_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	image = models.ImageField(upload_to='uploads/', blank=True, null=True)

	class Meta:
		ordering = ['location', 'locker_number']

	def __str__(self):
		return f"{self.location.name} - Locker #{self.locker_number} ({self.get_size_display()})"


class Booking(models.Model):
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('active', 'Active'),
		('completed', 'Completed'),
		('cancelled', 'Cancelled'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
	locker = models.ForeignKey(Locker, on_delete=models.CASCADE, related_name='bookings')
	start_date = models.DateField()
	end_date = models.DateField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
	total_price = models.DecimalField(max_digits=10, decimal_places=2)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	special_instructions = models.TextField(blank=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.user.username} - {self.locker} ({self.start_date} to {self.end_date})"

	def calculate_total_price(self):
		"""Calculate total price based on daily rate and number of days"""
		delta = self.end_date - self.start_date
		days = delta.days + 1  # Include both start and end dates
		return self.locker.daily_price * days

	def save(self, *args, **kwargs):
		if not self.total_price:
			self.total_price = self.calculate_total_price()
		super().save(*args, **kwargs)
		