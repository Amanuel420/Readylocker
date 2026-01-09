from django.contrib import admin
from .models import Customer, Location, Locker, Booking


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
	list_display = ['name', 'address']
	search_fields = ['name', 'address']


@admin.register(Locker)
class LockerAdmin(admin.ModelAdmin):
	list_display = ['locker_number', 'location', 'size', 'status', 'daily_price']
	list_filter = ['location', 'size', 'status']
	search_fields = ['locker_number', 'location__name']
	list_editable = ['status']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
	list_display = ['user', 'locker', 'start_date', 'end_date', 'status', 'total_price', 'created_at']
	list_filter = ['status', 'start_date', 'end_date']
	search_fields = ['user__username', 'locker__locker_number', 'locker__location__name']
	readonly_fields = ['total_price', 'created_at', 'updated_at']
	date_hierarchy = 'start_date'


admin.site.register(Customer)   
