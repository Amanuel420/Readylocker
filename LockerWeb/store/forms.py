from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm 
from django import forms
from .models import Booking, Locker, Location # Imported Location
from django.core.exceptions import ValidationError
from datetime import date


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'


class BookingForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'min': str(date.today())}),
        help_text='Select your booking start date'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'min': str(date.today())}),
        help_text='Select your booking end date'
    )
    special_instructions = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        help_text='Any special instructions or notes (optional)'
    )

    class Meta:
        model = Booking
        fields = ['start_date', 'end_date', 'special_instructions']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date < date.today():
                raise ValidationError("Start date cannot be in the past.")
            if end_date < start_date:
                raise ValidationError("End date must be after start date.")
            delta = end_date - start_date
            if delta.days > 365:
                raise ValidationError("Booking cannot exceed 365 days.")
        return cleaned_data

# --- NEW FORMS FOR SELLERS ---

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        # We exclude 'owner' because that is set automatically in the view
        fields = ['name', 'street_address', 'city', 'state', 'zip_code', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control mb-2'})
# inside forms.py

class LockerForm(forms.ModelForm):
    class Meta:
        model = Locker
        fields = ['locker_number', 'size', 'daily_price', 'status', 'description', 'image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make locker_number optional so auto-generation works
        self.fields['locker_number'].required = False
        self.fields['locker_number'].widget.attrs.update({
            'class': 'form-control mb-2', 
            'placeholder': 'Leave blank to auto-generate'
        })
        
        # Style other fields
        for field in self.fields:
            if field != 'locker_number':
                self.fields[field].widget.attrs.update({'class': 'form-control mb-2'})