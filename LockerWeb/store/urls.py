from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('about/', views.about, name="about"),
    path('login/', views.login_user, name="login"),
    path('register/', views.register_user, name="register"),
    path('logout/', views.logout_user, name="logout"),
    path('locker/<int:pk>/', views.locker_detail, name="locker_detail"),
    path('locker/<int:pk>/book/', views.book_locker, name="book_locker"),
    path('my-bookings/', views.my_bookings, name="my_bookings"),
    path('booking/<int:pk>/cancel/', views.cancel_booking, name="cancel_booking"),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms'),
    path('privacy-policy/', views.privacy_policy, name='privacy'),
]
