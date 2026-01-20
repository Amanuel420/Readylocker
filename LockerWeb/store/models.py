from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import datetime
import ssl
from geopy.geocoders import ArcGIS

class Category(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self): return self.name

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=100)
    def __str__(self): return f'{self.first_name} {self.last_name}'

class Location(models.Model):
    STATE_CHOICES = [
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
        ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
        ('DC', 'District of Columbia'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'),
        ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'),
        ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'),
        ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'),
        ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'),
        ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'),
        ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'),
        ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'),
        ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'),
        ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')
    ]

    name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255, verbose_name="Street Address")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, choices=STATE_CHOICES)
    zip_code = models.CharField(max_length=10, verbose_name="Zip Code")
    description = models.TextField(blank=True)
    
    # Coordinates
    latitude = models.FloatField(default=0.0, blank=True) 
    longitude = models.FloatField(default=0.0, blank=True)
    image = models.ImageField(upload_to='location_uploads/', blank=True, null=True)

    def __str__(self):
        return self.name
    
    @property
    def address(self):
        return f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"
    
    def save(self, *args, **kwargs):
        # Only attempt to find address if we have one
        if self.street_address and self.city:
            try:
                # FIX 1: Ignore SSL Certificate errors (Fixes your terminal error)
                ctx = ssl._create_unverified_context()
                
                # FIX 2: Use ArcGIS instead of Nominatim (Better for US addresses)
                geolocator = ArcGIS(user_agent="ready_locker_app_v4", ssl_context=ctx)
                
                # ATTEMPT 1: Exact Address
                location_string = f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"
                print(f"Trying Address: {location_string}")
                location = geolocator.geocode(location_string)
                
                # ATTEMPT 2: Fallback to Zip Code (If street is new/unknown)
                if not location:
                    print("  -> Exact address not found. Using Zip Code fallback...")
                    fallback_string = f"{self.city}, {self.state} {self.zip_code}"
                    location = geolocator.geocode(fallback_string)

                if location:
                    self.latitude = location.latitude
                    self.longitude = location.longitude
                    print(f"  -> SUCCESS! Mapped to: {self.latitude}, {self.longitude}")
                else:
                    print("  -> FAILED: Could not map this location.")
                    
            except Exception as e:
                print(f"Geocoding Error: {e}")
                
        super().save(*args, **kwargs)

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
    locker_number = models.CharField(max_length=20)
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
        unique_together = ('location', 'locker_number')

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
        delta = self.end_date - self.start_date
        days = delta.days + 1
        return self.locker.daily_price * days

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)