from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import (
    Category, Event_management, Speaker_management, Participant_management,
    Schedule_management, Payment, CartItem, User
)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'})
        }

class EventManagementForm(forms.ModelForm):
    class Meta:
        model = Event_management
        fields = ['title', 'description', 'start_date', 'end_date', 'location', 
                 'category', 'is_free', 'price', ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter event description'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event location'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter ticket price'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError("End date must be after start date")
        
        return cleaned_data

class SpeakerManagementForm(forms.ModelForm):
    class Meta:
        model = Speaker_management
        fields = ['name', 'biography', 'photo', 'email', 'phone_number', 
                 'linkedin_link', 'twitter_link']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter speaker name'}),
            'biography': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter speaker biography'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter speaker email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'linkedin_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter LinkedIn profile URL'}),
            'twitter_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter Twitter profile URL'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ParticipantManagementForm(forms.ModelForm):
    class Meta:
        model = Participant_management
        fields = ['name', 'email', 'phone_number','sex','university','Event']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter participant name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter participant email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'sex': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'enter F or M'}),
            'university': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your university'}),
            'Event': forms.Select(attrs={'class': 'form-control'}),
        }

class ScheduleManagementForm(forms.ModelForm):
    class Meta:
        model = Schedule_management
        fields = ['event', 'start_time', 'end_time', 'topic', 'speaker']
        widgets = {
            'event': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'topic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter session topic'}),
            'speaker': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time > end_time:
            raise ValidationError("End time must be after start time")
        
        return cleaned_data

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['participant', 'event', 'amount_paid', 'payment_method', 
                 'transaction_id', 'payment_status', ]
        widgets = {
            'participant': forms.Select(attrs={'class': 'form-control'}),
            'event': forms.Select(attrs={'class': 'form-control'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount paid'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter transaction ID'}),
            'payment_status': forms.Select(attrs={'class': 'form-control'}),
            'cardholder_name': forms.Select(attrs={'class': 'form-control'}),
            'card_number': forms.Select(attrs={'class': 'form-control'}),
            
        }

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['event', 'quantity']
        widgets = {
            'event': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise ValidationError("Quantity must be at least 1")
        return quantity

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 
                 'last_name', 'phone_number', 'address', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter address'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 
                 'address', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class EmailVerificationForm(forms.Form):
    verification_code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter verification code',
            'pattern': '[0-9]{6}',
            'title': 'Please enter a 6-digit code'
        })
    )
