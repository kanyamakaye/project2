from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Category, Event_management, Speaker_management, Participant_management,
    Schedule_management, Payment, CartItem, EmailVerification, User
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Event_management)
class EventManagementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'start_date', 'end_date', 'location', 'is_free', 'price', 'available_tickets')
    list_filter = ('category', 'is_free', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)

@admin.register(Speaker_management)
class SpeakerManagementAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number')
    search_fields = ('name', 'email', 'biography')
    list_filter = ('email',)

@admin.register(Participant_management)
class ParticipantManagementAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'user')
    search_fields = ('name', 'email', 'phone_number')
    list_filter = ('user',)

@admin.register(Schedule_management)
class ScheduleManagementAdmin(admin.ModelAdmin):
    list_display = ('event', 'topic', 'speaker', 'start_time', 'end_time')
    list_filter = ('event', 'speaker', 'start_time')
    search_fields = ('topic', 'event__title', 'speaker__name')
    date_hierarchy = 'start_time'
    ordering = ('-start_time',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'participant', 'event', 'amount_paid', 'payment_status', 'payment_date')
    list_filter = ('payment_status', 'payment_method', 'payment_date')
    search_fields = ('transaction_id', 'participant__name', 'event__title')
    date_hierarchy = 'payment_date'
    ordering = ('-payment_date',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'quantity', 'date_added', 'total_price')
    list_filter = ('date_added',)
    search_fields = ('user__username', 'event__title')
    date_hierarchy = 'date_added'
    ordering = ('-date_added',)

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'is_verified')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'code')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_email_verified')
    list_filter = ('is_staff', 'is_active', 'is_email_verified', 'is_admin', 'is_speaker', 'is_participant')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin', 'is_speaker', 'is_participant', 'is_email_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    ordering = ('-date_joined',)

