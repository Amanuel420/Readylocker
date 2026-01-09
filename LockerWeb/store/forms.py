from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm 
from django import forms
from .models import Booking, Locker
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
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


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
			
			# Check if booking is too long (optional: max 365 days)
			delta = end_date - start_date
			if delta.days > 365:
				raise ValidationError("Booking cannot exceed 365 days.")

		return cleaned_data