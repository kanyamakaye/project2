from django.db import models
from django.contrib.auth.models import User, AbstractUser, Permission
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from datetime import timedelta
from django.utils import timezone
from geopy.geocoders import Nominatim

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Event_management(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    available_tickets = models.PositiveIntegerField(default=0)
   

    def __str__(self):
        return self.title

class Speaker_management(models.Model):
    name = models.CharField(max_length=100)
    biography = models.TextField()
    photo = models.ImageField(upload_to='speakers/', blank=True, null=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    linkedin_link = models.URLField(blank=True)
    twitter_link = models.URLField(blank=True)

    def __str__(self):
        return self.name

class Participant_management(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    sex = models.CharField(max_length=1)
    university = models.CharField(max_length=200)
    Event = models.ForeignKey(Event_management, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Schedule_management(models.Model):
    event = models.ForeignKey(Event_management, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    topic = models.CharField(max_length=150)
    speaker = models.ForeignKey(Speaker_management, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.topic

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed')
    ]
     # Payment method choices
    PAYMENT_METHOD_CHOICES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('PAYPAL', 'PayPal'),
        ('CASH', 'Cash'),
    ]

    participant = models.ForeignKey(Participant_management, on_delete=models.CASCADE)
    event = models.ForeignKey(Event_management, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)
    card_number = models.CharField(max_length=19, blank=True, null=True)  # Stored securely or masked
    cardholder_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.transaction_id

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event_management, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} ticket(s) for {self.event.title}"
    
    @property
    def total_price(self):
        return self.quantity * self.event.price

class EmailVerification(models.Model):
    """Model for storing email verification codes"""
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Verification for {self.user.email}"
    
    def is_valid(self):
        """Check if verification code is still valid (within 15 minutes)"""
        return (timezone.now() - self.created_at) < timedelta(minutes=15)
    
    def send_verification_email(self):
        """Send verification email to user"""
        subject = 'Email Verification Code'
        message = f'Your verification code is: {self.code}\nThis code will expire in 15 minutes.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [self.user.email]
        
        send_mail(subject, message, from_email, recipient_list)
    
    @classmethod
    def generate_code(cls):
        """Generate a 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=6))

class User(AbstractUser):
    """Custom User model extending Django's AbstractUser
    
    This model extends Django's built-in User model with additional fields and functionality
    specific to the event management system.
    
    Reverse Accessors:
    - Groups: Use group.event_user_set instead of group.user_set
    - Permissions: Use permission.event_user_set instead of permission.user_set
    - Queries: Use group__event_user and permission__event_user in filters
    
    Example Usage:
        # Get all users in a specific group
        group = Group.objects.get(name='Event Organizers')
        organizers = group.event_user_set.all()
        
        # Get users with specific permission
        permission = Permission.objects.get(codename='add_event')
        users_with_permission = permission.event_user_set.all()
        
        # Filter users by group
        admin_users = User.objects.filter(groups__name='Administrators')
        
        # Filter users by permission
        users_can_add_events = User.objects.filter(user_permissions__codename='add_event')
    """
    
    # Additional fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_speaker = models.BooleanField(default=False)
    is_participant = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)
    
    # Profile picture
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text=_('Upload your profile picture')
    )
    
    # Additional metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Resolve reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name='event_user_set',
        related_query_name='event_user',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='event_user_set',
        related_query_name='event_user',
    )
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.get_full_name()})"
    
    def get_role(self):
        """Get the user's role based on their permissions"""
        if self.is_admin:
            return "Admin"
        elif self.is_speaker:
            return "Speaker"
        else:
            return "Participant"
    
    def get_profile_picture_url(self):
        """Get the URL of the user's profile picture"""
        if self.profile_picture:
            return self.profile_picture.url
        return None
    
    @classmethod
    def get_users_by_group(cls, group_name):
        """Get all users belonging to a specific group
        
        Args:
            group_name (str): Name of the group
            
        Returns:
            QuerySet: Users in the specified group
        """
        return cls.objects.filter(groups__name=group_name)
    
    @classmethod
    def get_users_by_permission(cls, permission_codename):
        """Get all users with a specific permission
        
        Args:
            permission_codename (str): Codename of the permission
            
        Returns:
            QuerySet: Users with the specified permission
        """
        return cls.objects.filter(user_permissions__codename=permission_codename)
    
    @classmethod
    def get_users_by_group_and_permission(cls, group_name, permission_codename):
        """Get users who belong to a specific group and have a specific permission
        
        Args:
            group_name (str): Name of the group
            permission_codename (str): Codename of the permission
            
        Returns:
            QuerySet: Users matching both criteria
        """
        return cls.objects.filter(
            groups__name=group_name,
            user_permissions__codename=permission_codename
        ).distinct()
    
    def has_group_permission(self, permission_codename):
        """Check if user has a permission through their groups
        
        Args:
            permission_codename (str): Codename of the permission to check
            
        Returns:
            bool: True if user has the permission through any of their groups
        """
        return self.groups.filter(
            permissions__codename=permission_codename
        ).exists()
    
    def get_all_permissions(self):
        """Get all permissions the user has, both directly and through groups
        
        Returns:
            set: Set of permission codenames
        """
        # Get direct permissions
        direct_permissions = set(
            self.user_permissions.values_list('codename', flat=True)
        )
        
        # Get permissions through groups
        group_permissions = set(
            Permission.objects.filter(
                group__event_user=self
            ).values_list('codename', flat=True)
        )
        
        return direct_permissions.union(group_permissions)

    # Credential-related methods
    def verify_credentials(self, password):
        """Verify user credentials
        
        Args:
            password (str): Password to verify
            
        Returns:
            bool: True if credentials are valid
        """
        return self.check_password(password)
    
    def update_credentials(self, new_password):
        """Update user password
        
        Args:
            new_password (str): New password to set
        """
        self.set_password(new_password)
        self.save()
    
    def get_credential_info(self):
        """Get user credential information
        
        Returns:
            dict: Dictionary containing credential-related information
        """
        return {
            'username': self.username,
            'email': self.email,
            'last_login': self.last_login,
            'is_active': self.is_active,
            'is_staff': self.is_staff,
            'is_superuser': self.is_superuser,
            'role': self.get_role(),
            'has_password': bool(self.password),
            'groups': list(self.groups.values_list('name', flat=True)),
            'permissions': list(self.get_all_permissions())
        }
    
    @classmethod
    def authenticate_user(cls, username, password):
        """Authenticate user with credentials
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            User: Authenticated user if successful, None otherwise
        """
        try:
            user = cls.objects.get(username=username)
            if user.check_password(password):
                return user
        except cls.DoesNotExist:
            pass
        return None
    
    # Two-factor authentication methods
    def send_verification_code(self):
        """Send verification code to user's email"""
        # Delete any existing verification codes
        EmailVerification.objects.filter(user=self).delete()
        
        # Create new verification code
        verification = EmailVerification.objects.create(
            user=self,
            code=EmailVerification.generate_code()
        )
        
        # Send verification email
        verification.send_verification_email()
        return verification.code
    
    def verify_email(self, code):
        """Verify email with provided code
        
        Args:
            code (str): Verification code
            
        Returns:
            bool: True if verification successful
        """
        try:
            verification = EmailVerification.objects.get(
                user=self,
                code=code,
                is_verified=False
            )
            
            if verification.is_valid():
                verification.is_verified = True
                verification.save()
                self.is_email_verified = True
                self.save()
                return True
        except EmailVerification.DoesNotExist:
            pass
        return False
    
    def is_authenticated_with_2fa(self):
        """Check if user is authenticated with two-factor authentication
        
        Returns:
            bool: True if user has verified email
        """
        return self.is_email_verified
    