from django.urls import path
from . import views

urlpatterns = [
    # Main Pages
    path("", views.home, name="home"),
    path('about/', views.about, name="about"),
    
    # Auth
    path('login/', views.login_user, name="login"),
    path('register/', views.register_user, name="register"),
    path('logout/', views.logout_user, name="logout"),
    
    # Booking Flow
    path('location/<int:pk>/', views.location_detail, name='location_detail'),
    path('book/<int:location_id>/<str:size>/', views.book_cabinet, name='book_cabinet'),
    
    # User Dashboard
    path('my-bookings/', views.my_bookings, name="my_bookings"),
    path('booking/<int:pk>/cancel/', views.cancel_booking, name="cancel_booking"),
    
    # Legal
    path('terms-and-conditions/', views.terms_and_conditions, name='terms'),
    path('privacy-policy/', views.privacy_policy, name='privacy'),
]