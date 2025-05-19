import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.db.models import Count, Sum, Avg, Min, Max
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth.forms import AuthenticationForm
from .forms import (
    EventManagementForm, SpeakerManagementForm, ParticipantManagementForm,
    ScheduleManagementForm, CategoryForm, PaymentForm, CartItemForm,
    UserRegistrationForm, UserProfileForm, EmailVerificationForm
)
from .models import (
    Category, Event_management, Speaker_management, Participant_management,
    Schedule_management, Payment, User, CartItem, EmailVerification
)
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import json

# Configure logger with more detailed settings
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler
file_handler = logging.FileHandler('event_app.log')
file_handler.setLevel(logging.INFO)

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(file_handler)


def json_view(request):
    data = list(Category.objects.values(), Event_management.objects.values(), 
                Speaker_management.objects.values(), Participant_management.objects.values(), 
                Schedule_management.objects.values(), Payment.objects.values())
    return JsonResponse(data, safe=False)


def home(request):
    try:
        # Get upcoming events
        upcoming_events = Event_management.objects.filter(
            start_date__gte=timezone.now()
        ).select_related('category').prefetch_related('speaker_management_set')[:6]

        # Get free events
        free_events = Event_management.objects.filter(
            is_paid=False,
            start_date__gte=timezone.now()
        ).select_related('category').prefetch_related('speaker_management_set')[:3]

        # Get event statistics
        total_events = Event_management.objects.count()
        upcoming_count = Event_management.objects.filter(start_date__gte=timezone.now()).count()
        past_count = total_events - upcoming_count

        context = {
            'upcoming_events': upcoming_events,
            'free_events': free_events,
            'total_events': total_events,
            'upcoming_count': upcoming_count,
            'past_count': past_count,
        }
        return render(request, 'home.html', context)
    except Exception as e:
        logger.error(f"Error in home view: {str(e)}")
        return render(request, 'home.html', {'error': 'An error occurred while loading the page.'})


def events_list(request):
    events = Event_management.objects.all()
    return render(request, 'event.html', {'events': events})

def admin_dashboard(request):
    return render(request,'index.html')
def speaker_list(request):
    speaker_list = Speaker_management.objects.all()
    paginator = Paginator(speaker_list, 10)  # Show 10 speakers per page
    page = request.GET.get('page')
    
    try:
        speakers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        speakers = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        speakers = paginator.page(paginator.num_pages)
        
    return render(request, 'speaker.html', {'speakers': speakers})

def details_of_speaker(request, id):
    speaker = get_object_or_404(Speaker_management, id=id)
    return render(request, 'speaker_details.html', {'speaker': speaker})


def event_details(request, event_title):
    event = get_object_or_404(Event_management, title=event_title)
    return render(request, 'event_details.html', {'event': event})

def paid_events(request):
    """View for displaying all paid events with their details."""
    try:
        # Get all paid events with related data
        paid_events = Event_management.objects.filter(
            is_paid=True
        ).select_related(
            'category'
        ).prefetch_related(
            'speaker_management_set'
        ).order_by('-start_date')
        
        # Get current date for filtering upcoming events
        current_date = timezone.now().date()
        
        # Apply category filter if provided
        category_id = request.GET.get('category')
        if category_id:
            paid_events = paid_events.filter(category_id=category_id)
        
        # Separate upcoming and past paid events
        upcoming_events = paid_events.filter(start_date__gte=current_date)
        past_events = paid_events.filter(end_date__lt=current_date)
        
        # Get statistics
        total_paid_events = paid_events.count()
        upcoming_count = upcoming_events.count()
        past_count = past_events.count()
        
        # Get categories for filtering
        categories = Category.objects.filter(
            event_management__is_paid=True
        ).distinct()
        
        context = {
            'paid_events': paid_events,
            'upcoming_events': upcoming_events,
            'past_events': past_events,
            'total_paid_events': total_paid_events,
            'upcoming_count': upcoming_count,
            'past_count': past_count,
            'categories': categories,
            'selected_category': int(category_id) if category_id else None,
            'timezone': timezone.now()
        }
        
        return render(request, 'paid_events.html', context)
        
    except Exception as e:
        logger.error(f"Error in paid_events view: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while loading paid events. Please try again later.")
        return redirect('home')


def upcoming(request):
    current_date = timezone.now().date()
    upcoming = Event_management.objects.filter(start_date__gte=current_date)
    return render(request, 'upcoming.html', {'upcoming': upcoming})


def free_events(request):
    """View for displaying all free events."""
    try:
        # Get all free events with related data
        free_events = Event_management.objects.filter(
            is_free=True
        ).select_related(
            'category'
        ).prefetch_related(
            'speaker_management_set'
        ).order_by('-start_date')
        
        # Get current date for filtering upcoming events
        current_date = timezone.now().date()
        
        # Apply category filter if provided
        category_id = request.GET.get('category')
        if category_id:
            free_events = free_events.filter(category_id=category_id)
        
        # Separate upcoming and past free events
        upcoming_events = free_events.filter(start_date__gte=current_date)
        past_events = free_events.filter(end_date__lt=current_date)
        
        # Get statistics
        total_free_events = free_events.count()
        upcoming_count = upcoming_events.count()
        past_count = past_events.count()
        
        # Get categories for filtering
        categories = Category.objects.filter(
            event_management__is_free=True
        ).distinct()
        
        context = {
            'upcoming_events': upcoming_events,
            'past_events': past_events,
            'total_free_events': total_free_events,
            'upcoming_count': upcoming_count,
            'past_count': past_count,
            'categories': categories,
            'selected_category': int(category_id) if category_id else None,
        }
        
        return render(request, 'free_events.html', context)
        
    except Exception as e:
        logger.error(f"Error in free_events view: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while loading free events. Please try again later.")
        return redirect('home')

def participants_with_all_payments(request):
    participants = Participant_management.objects.annotate(
        payment_count=Count('payment')
    ).filter(
        payment_count=Event_management.objects.count(),
        payment_count__gt=0
    )
    return render(request, 'participants_with_all_payments.html', {'participants': participants})

#def participant_list(request):
def participant_list(request):
    """
    Display a simple list of all participants.
    """
    # Get all participants
    participants = Participant_management.objects.all()
    
    # Pass to template
    context = {
        'participants': participants,
        'total_count': participants.count()
    }
    
    return render(request, 'participant_list.html', context)
def event_forms(request):
    if request.method == 'POST':
        form = EventManagementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event created successfully!')
            return redirect('events_list')
    else:
        form = EventManagementForm()
    return render(request, 'Event_forms.html', {'form': form})

def speaker_forms(request):
    if request.method == 'POST':
        form = SpeakerManagementForm(request.POST, request.FILES)
        if form.is_valid():
            speaker = form.save()
            messages.success(request, f'Speaker "{speaker.name}" added successfully!')
            return redirect('speaker_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SpeakerManagementForm()
    
    # Get all speakers for the table, ordered by most recent first
    speakers = Speaker_management.objects.all().order_by('-id')[:5]
    
    # Add error handling for the table
    try:
        context = {
            'form': form,
            'speakers': speakers,
            'error': None
        }
    except Exception as e:
        context = {
            'form': form,
            'speakers': [],
            'error': str(e)
        }
    
    return render(request, 'speaker_form.html', context)

def participant_forms(request):
    if request.method == 'POST':
        form = ParticipantManagementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Participant added successfully!')
            return redirect('participant_list')
    else:
        form = ParticipantManagementForm()
    return render(request, 'participant_form.html', {'form': form})

def schedule_forms(request):
   form = ScheduleManagementForm(request.POST or None)
   if form.is_valid():
            form.save()
            form = ScheduleManagementForm()  
            messages.success(request, 'Schedule created successfully!')
            return redirect('display_schedule')  # Redirect after successful form submission
   context = {
            'form': form
        }   
   return render(request, 'scheduleform.html', context)  # Changed from 'sheduleform.html' to 'scheduleform.html'

def display_schedule(request):
    schedules = Schedule_management.objects.all()
    return render(request, 'schedulelist.html', {'schedules': schedules})

def display_category(request):
    categories = Category.objects.all()
    return render(request, 'categorylist.html', {'categories': categories})

def cat_forms(request):
   form =CategoryForm(request.POST or None)
   if form.is_valid():
            form.save()
            form=CategoryForm() 
   context = {
            'form': form
              
        }   
   return render (request, 'categoryform.html',{'form':form})

def categories(request):
    categories =Category.objects.all()
    return render(request, 'categorylist.html', {'categories': categories})

def all_payments(request):
    """
    Display all payments with related event and participant information.
    """
    try:
        # Get all payments with related event and participant data
        payments = Payment.objects.select_related(
            'event',
            'participant'
        ).order_by('-payment_date')

        # Calculate payment statistics
        payment_stats = {
            'total_amount': payments.aggregate(Sum('amount'))['amount__sum'] or 0,
            'total_payments': payments.count(),
            'paid_count': payments.filter(payment_status='PAID').count(),
            'pending_count': payments.filter(payment_status='PENDING').count(),
            'failed_count': payments.filter(payment_status='FAILED').count(),
        }

        context = {
            'payments': payments,
            'payment_stats': payment_stats,
        }
        return render(request, 'all_payments.html', context)
    except Exception as e:
        logger.error(f"Error in all_payments view: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while loading payments. Please try again later.")
        return redirect('home')

def participant_payments(request, participant_id):
    participant = get_object_or_404(Participant_management, id=participant_id)
    payments = Payment.objects.filter(participant=participant)
    return render(request, 'participant_payments.html', {'participant': participant, 'payments': payments})

def event_count(request):
    """View to display total count of events"""
    total_events = Event_management.objects.count()
    context = {
        'total_events': total_events,
        'title': 'Event Count'
    }
    return render(request, 'event_count.html', context)

def total_paid_event(request, event_id):
    event = get_object_or_404(Event_management, id=event_id)
    total_paid = Payment.objects.filter(event=event).aggregate(total=Sum('amount_paid'))['total']
    return render(request, 'total_paid_event.html', {'event': event, 'total_paid': total_paid})

def avg_price_paid(request):
    paid_events = Event_management.objects.filter(is_free=False)
    avg_price = paid_events.aggregate(avg=Avg('payment__amount_paid'))['avg']
    return render(request, 'avg_price_paid.html', {'avg_price': avg_price})


def highest_paid_events(request):
    """View for displaying events with highest prices."""
    events = Event_management.objects.filter(is_paid=True).order_by('-price')[:10]
    context = {'events': events}
    return render(request, 'analytics/highest_paid.html', context)

def top_paying_participants(request):
    participants = Participant_management.objects.annotate(
        total_paid=Sum('payment__amount_paid')
    ).filter(
        total_paid__isnull=False
    ).order_by('-total_paid')[:10]
    return render(request, 'top_paying_participants.html', {'participants': participants})

def recent_payers(request):
    recent_date = timezone.now() - timezone.timedelta(days=7)
    participants = Participant_management.objects.filter(
        payment__payment_date__gte=recent_date
    ).distinct()
    return render(request, 'recent_payers.html', {'participants': participants})

def top_revenue_events(request):
    events = Event_management.objects.all()
    events_with_revenue = [(event, Payment.objects.filter(event=event).aggregate(total=Sum('amount_paid'))['total']) for event in events]
    events_with_revenue.sort(key=lambda x: x[1] if x[1] is not None else 0, reverse=True)

    return render(request, 'top_revenue_events.html', {'events_with_revenue': events_with_revenue})

def participants_paid_all(request):
    all_events = Event_management.objects.all()
    participants = Payment.objects.values('participant').distinct()
    participants_paid_all_events = []

    for participant in participants:
        paid_events = Payment.objects.filter(participant=participant['participant'])
        if paid_events.count() == all_events.count():
            participants_paid_all_events.append(participant['participant'])

    return render(request, 'participants_paid_all.html', {'participants_paid_all_events': participants_paid_all_events})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            if 'profile_picture' in request.FILES:
                profile_picture = request.FILES['profile_picture']
                fs = FileSystemStorage()
                filename = fs.save(f'profile_pictures/{user.username}_{profile_picture.name}', profile_picture)
                user.profile_picture = filename
                user.save()
            verification_code = user.send_verification_code()
            request.session['verification_user_id'] = user.id
            messages.info(request, 'Please check your email for the verification code.')
            return redirect('verify_email')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def verify_email(request):
    user_id = request.session.get('verification_user_id')
    if not user_id:
        messages.error(request, 'Invalid verification session.')
        return redirect('register')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['verification_code']
            if user.verify_email(code):
                login(request, user)
                messages.success(request, 'Email verified successfully!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid or expired verification code.')
    else:
        form = EmailVerificationForm()
    
    return render(request, 'registration/verify_email.html', {'form': form})

def resend_verification(request):
    user_id = request.session.get('verification_user_id')
    if not user_id:
        messages.error(request, 'Invalid verification session.')
        return redirect('register')
    
    user = get_object_or_404(User, id=user_id)
    user.send_verification_code()
    messages.info(request, 'New verification code sent to your email.')
    return redirect('verify_email')

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


def profile(request):
    """View for displaying and updating user profile."""
    try:
        if request.method == 'POST':
            form = UserProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile was successfully updated!')
                return redirect('profile')
        else:
            form = UserProfileForm(instance=request.user)

        # Get user's events and payments
        user_events = Event_management.objects.filter(
            payment__participant__user=request.user
        ).distinct()
        
        user_payments = Payment.objects.filter(
            participant__user=request.user
        ).select_related('event')

        context = {
            'form': form,
            'user_events': user_events,
            'user_payments': user_payments,
        }
        return render(request, 'profile.html', context)
    except Exception as e:
        logger.error(f"Error in profile view: {str(e)}")
        messages.error(request, "An error occurred while loading your profile.")
        return redirect('home')

def participant_categories(request):
    categories = Category.objects.annotate(
        participant_count=Count('event_management__participant_management')
    ).order_by('-participant_count')
    return render(request, 'participant_categories.html', {'categories': categories})

def participants_by_category(request, category_id):
    """View for displaying participants in a specific category."""
    try:
        # Get the category
        category = get_object_or_404(Category, id=category_id)
        
        # Get participants who have paid for events in this category
        participants = Participant_management.objects.filter(
            payment__event__category=category
        ).select_related('user').prefetch_related(
            'payment_set__event'
        ).distinct()
        
        # Apply search filter if provided
        search_query = request.GET.get('search')
        if search_query:
            participants = participants.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            )
        
        # Apply status filter if provided
        status = request.GET.get('status')
        if status == 'active':
            participants = participants.filter(payment__payment_status='PAID')
        elif status == 'inactive':
            participants = participants.exclude(payment__payment_status='PAID')
        
        # Pagination
        paginator = Paginator(participants, 10)  # Show 10 participants per page
        page = request.GET.get('page')
        try:
            participants = paginator.page(page)
        except PageNotAnInteger:
            participants = paginator.page(1)
        except EmptyPage:
            participants = paginator.page(paginator.num_pages)
        
        # Calculate statistics
        active_participants = Participant_management.objects.filter(
            payment__event__category=category,
            payment__payment_status='PAID'
        ).distinct().count()
        
        total_events = Event_management.objects.filter(
            category=category,
            payment__payment_status='PAID'
        ).distinct().count()
        
        context = {
            'category': category,
            'participants': participants,
            'active_participants': active_participants,
            'total_events': total_events,
            'search_query': search_query,
            'status': status,
        }
        
        return render(request, 'participants_by_category.html', context)
        
    except Exception as e:
        logger.error(f"Error in participants_by_category view: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while loading participants. Please try again later.")
        return redirect('categories')

def admin_analytics(request):
    """Admin analytics dashboard view"""
    try:
        # Event statistics
        total_events = Event_management.objects.count()
        paid_events = Event_management.objects.filter(is_paid=True).count()
        free_events = total_events - paid_events
        
        # Participant statistics
        total_participants = Participant_management.objects.count()
        active_participants = Participant_management.objects.filter(
            payment__payment_status='PAID'
        ).distinct().count()
        
        # Payment statistics
        total_revenue = Payment.objects.filter(payment_status='PAID').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Recent activities
        recent_payments = Payment.objects.select_related(
            'participant', 'event'
        ).order_by('-payment_date')[:5]
        
        context = {
            'total_events': total_events,
            'paid_events': paid_events,
            'free_events': free_events,
            'total_participants': total_participants,
            'active_participants': active_participants,
            'total_revenue': total_revenue,
            'recent_payments': recent_payments,
        }
        return render(request, 'admin_analytics.html', context)
    except Exception as e:
        logger.error(f"Error in admin_analytics view: {str(e)}")
        messages.error(request, "An error occurred while loading analytics.")
        return redirect('home')
    
def admin_events(request):
    """Admin view for managing all events"""
    try:
        # Get all categories for the filter dropdown
        categories = Category.objects.all()
        
        # Base query
        events = Event_management.objects.select_related('category').all()
        
        # Apply filters
        search_query = request.GET.get('search')
        if search_query:
            events = events.filter(title__icontains=search_query)
            
        category_id = request.GET.get('category')
        if category_id:
            events = events.filter(category_id=category_id)
            
        status = request.GET.get('status')
        if status == 'upcoming':
            events = events.filter(start_date__gte=timezone.now())
        elif status == 'past':
            events = events.filter(end_date__lt=timezone.now())
            
        context = {
            'events': events,
            'categories': categories,
        }
        return render(request, 'admin_events.html', context)
    except Exception as e:
        logger.error(f"Error in admin_events view: {str(e)}")
        messages.error(request, "An error occurred while loading events.")
        return redirect('admin_home')

def admin_paid_events(request):
    """Admin view for managing paid events"""
    paid_events = Event_management.objects.filter(is_paid=True).select_related('category')
    return render(request, 'admin_paid_events.html', {'paid_events': paid_events})


def admin_free_events(request):
    """Admin view for managing free events"""
    free_events = Event_management.objects.filter(is_paid=False).select_related('category')
    return render(request, 'admin_free_events.html', {'free_events': free_events})


def admin_participants(request):
    """Admin view for managing participants"""
    try:
        # Get all participants with related data
        participants = Participant_management.objects.select_related('user').prefetch_related(
            'payment_set__event'
        ).all()
        
        # Get participants with payments
        participants_with_payments = participants.filter(payment__isnull=False).distinct()
        
        # Calculate statistics
        total_participants = participants.count()
        active_participants = participants_with_payments.count()
        
        context = {
            'participants': participants,
            'participants_with_payments': participants_with_payments,
            'total_participants': total_participants,
            'active_participants': active_participants,
        }
        
        return render(request, 'admin_participants.html', context)
    except Exception as e:
        logger.error(f"Error in admin_participants view: {str(e)}")
        messages.error(request, "An error occurred while loading participants.")
        return redirect('admin_home')
def admin_speakers(request):
    """Admin view for managing speakers"""
    speakers = Speaker_management.objects.all()
    return render(request, 'admin_speakers.html', {'speakers': speakers})

def admin_categories(request):
    """Admin view for managing categories"""
    categories = Category.objects.annotate(
        event_count=Count('event_management')
    ).all()
    return render(request, 'admin_categories.html', {'categories': categories})

def admin_schedule(request):
    """Admin view for managing schedules"""
    schedules = Schedule_management.objects.select_related('event').all()
    return render(request, 'admin_schedule.html', {'schedules': schedules})


def admin_payments(request):
    """Admin view for managing payments"""
    payments = Payment.objects.select_related(
        'participant', 'event'
    ).order_by('-payment_date')
    return render(request, 'admin_payments.html', {'payments': payments})

def average_price_analytics(request):
    """View for displaying average price analytics."""
    try:
        # Calculate average prices by category
        category_avg_prices = Category.objects.annotate(
            avg_price=Avg('event_management__price')
        ).filter(avg_price__isnull=False).order_by('-avg_price')

        # Calculate overall average price
        overall_avg_price = Event_management.objects.aggregate(
            avg_price=Avg('price')
        )['avg_price']

        context = {
            'category_avg_prices': category_avg_prices,
            'overall_avg_price': overall_avg_price,
        }
        return render(request, 'analytics/average_price.html', context)
    except Exception as e:
        logger.error(f"Error in average_price_analytics view: {str(e)}")
        messages.error(request, "An error occurred while loading analytics.")
        return redirect('home')


def top_revenue_events(request):
    """View for displaying events that generated the most revenue."""
    events = Event_management.objects.annotate(
        total_revenue=Sum('payment__amount')
    ).order_by('-total_revenue')[:10]
    context = {'events': events}
    return render(request, 'analytics/top_revenue.html', context)


def event_statistics(request):
    """View for displaying comprehensive event statistics."""
    total_events = Event_management.objects.count()
    paid_events = Event_management.objects.filter(is_paid=True).count()
    free_events = Event_management.objects.filter(is_paid=False).count()
    upcoming_events = Event_management.objects.filter(date__gt=timezone.now()).count()
    
    # Get events by category with proper data formatting
    events_by_category = Event_management.objects.values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Prepare data for the chart
    category_labels = json.dumps([item['category__name'] or 'Uncategorized' for item in events_by_category])
    category_values = json.dumps([item['count'] for item in events_by_category])
    
    context = {
        'total_events': total_events,
        'paid_events': paid_events,
        'free_events': free_events,
        'upcoming_events': upcoming_events,
        'events_by_category': events_by_category,
        'category_labels': category_labels,
        'category_values': category_values,
    }
    return render(request, 'analytics/event_statistics.html', context)


def participant_statistics(request):
    """View for displaying participant statistics."""
    try:
        # Get total participants
        total_participants = Participant_management.objects.count()

        # Get participants by category
        participants_by_category = Category.objects.annotate(
            participant_count=Count('event_management__payment__participant', distinct=True)
        ).order_by('-participant_count')

        # Get payment status statistics
        payment_stats = Payment.objects.aggregate(
            total_payments=Count('id'),
            paid_count=Count('id', filter=Q(payment_status='PAID')),
            pending_count=Count('id', filter=Q(payment_status='PENDING')),
            failed_count=Count('id', filter=Q(payment_status='FAILED'))
        )

        context = {
            'total_participants': total_participants,
            'participants_by_category': participants_by_category,
            'payment_stats': payment_stats,
        }
        return render(request, 'analytics/participant_stats.html', context)
    except Exception as e:
        logger.error(f"Error in participant_statistics view: {str(e)}")
        messages.error(request, "An error occurred while loading statistics.")
        return redirect('home')

def edit_participant(request, participant_id):
    participant = get_object_or_404(Participant_management, id=participant_id)
    if request.method == 'POST':
        form = ParticipantManagementForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Participant updated successfully!')
            return redirect('participant_list')
    else:
        form = ParticipantManagementForm(instance=participant)
    return render(request, 'participant_form.html', {'form': form, 'participant': participant})

def delete_participant(request, participant_id):
    participant = get_object_or_404(Participant_management, id=participant_id)
    if request.method == 'POST':
        participant.delete()
        messages.success(request, 'Participant deleted successfully!')
        return redirect('participant_list')
    return render(request, 'confirm_delete.html', {'participant': participant})


def participant_payments(request):
    """View for displaying all participant payments."""
    try:
        # Get all payments with related participant and event information
        payments = Payment.objects.select_related(
            'participant',
            'event'
        ).order_by('-payment_date')
        
        # Apply filters if provided
        participant_id = request.GET.get('participant')
        if participant_id:
            payments = payments.filter(participant_id=participant_id)
            
        event_id = request.GET.get('event')
        if event_id:
            payments = payments.filter(event_id=event_id)
            
        status = request.GET.get('status')
        if status:
            payments = payments.filter(payment_status=status)
        
        # Pagination
        paginator = Paginator(payments, 10)  # Show 10 payments per page
        page = request.GET.get('page')
        try:
            payments = paginator.page(page)
        except PageNotAnInteger:
            payments = paginator.page(1)
        except EmptyPage:
            payments = paginator.page(paginator.num_pages)
            
        context = {
            'payments': payments,
            'total_payments': paginator.count,
            'participant_id': participant_id,
            'event_id': event_id,
            'status': status,
        }
        
        return render(request, 'participant_payments.html', context)
        
    except Exception as e:
        logger.error(f"Error in participant_payments view: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while loading payments. Please try again later.")
        return redirect('home')

def edit_category(request, category_id):
    """View for editing an existing category."""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('display_category')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'categoryform.html', {
        'form': form,
        'category': category,
        'title': 'Edit Category'
    })

def delete_category(request, category_id):
    """View for deleting a category."""
    category = get_object_or_404(Category, id=category_id)
    
    try:
        # Check if the category is being used by any events
        if category.event_management_set.exists():
            messages.error(request, 'Cannot delete category. It is being used by one or more events.')
            return redirect('display_category')
        
        category.delete()
        messages.success(request, 'Category deleted successfully!')
    except Exception as e:
        logger.error(f"Error deleting category: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while deleting the category.')
    
    return redirect('display_category')

def categories(request):
    """View for displaying all categories."""
    try:
        categories = Category.objects.annotate(
            event_count=Count('event_management')
        ).order_by('name')
        return render(request, 'categories.html', {'categories': categories})
    except Exception as e:
        logger.error(f"Error in categories view: {str(e)}")
        messages.error(request, "An error occurred while loading categories.")
        return redirect('home')


#sample to test
def dashboard_summary(request):
    """API endpoint for dashboard summary statistics"""
    total_events = Event_management.objects.count()
    total_participants = Participant_management.objects.count()
    total_revenue = Payment.objects.filter(payment_status='PAID').aggregate(
        total=Sum('amount_paid'))['total'] or 0
    total_speakers = Speaker_management.objects.count()
    
    return JsonResponse({
        'total_events': total_events,
        'total_participants': total_participants,
        'total_revenue': float(total_revenue),
        'total_speakers': total_speakers
    })

def dashboard_registrations(request):
    """API endpoint for registration data over the last 6 months"""
    today = timezone.now().date()
    six_months_ago = today - timedelta(days=180)
    
    # Get the last 6 months as labels
    months = []
    month_data = {}
    
    for i in range(5, -1, -1):
        month = today.replace(day=1) - timedelta(days=i*30)
        month_name = month.strftime('%B')
        months.append(month_name)
        month_data[month_name] = {'paid': 0, 'free': 0}
    
    # Get registration data
    payments = Payment.objects.filter(
        payment_date__gte=six_months_ago,
        payment_status='PAID'
    ).select_related('event')
    
    for payment in payments:
        month_name = payment.payment_date.strftime('%B')
        if month_name in month_data:
            if payment.event.is_free:
                month_data[month_name]['free'] += 1
            else:
                month_data[month_name]['paid'] += 1
    
    paid_registrations = [month_data[month]['paid'] for month in months]
    free_registrations = [month_data[month]['free'] for month in months]
    
    # Calculate trend
    current_month_total = paid_registrations[-1] + free_registrations[-1]
    prev_month_total = paid_registrations[-2] + free_registrations[-2]
    
    if prev_month_total > 0:
        percent_change = ((current_month_total - prev_month_total) / prev_month_total) * 100
        trend = f"{'Up' if percent_change >= 0 else 'Down'} by {abs(percent_change):.1f}% from last month"
    else:
        trend = "No data from previous month for comparison"
    
    return JsonResponse({
        'months': months,
        'paid_registrations': paid_registrations,
        'free_registrations': free_registrations,
        'trend': trend
    })

def dashboard_revenue(request):
    """API endpoint for revenue by category"""
    # Get revenue by category
    categories = Category.objects.all()
    category_revenue = []
    category_names = []
    
    for category in categories:
        revenue = Payment.objects.filter(
            event__category=category,
            payment_status='PAID'
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        category_names.append(category.name)
        category_revenue.append(float(revenue))
    
    # Find highest revenue category
    if category_revenue:
        max_revenue_index = category_revenue.index(max(category_revenue))
        max_category = category_names[max_revenue_index]
        
        # Calculate percentage difference from average
        avg_revenue = sum(category_revenue) / len(category_revenue)
        percent_diff = ((max(category_revenue) - avg_revenue) / avg_revenue) * 100 if avg_revenue > 0 else 0
        
        trend = f"{max_category} events lead by {percent_diff:.1f}%"
    else:
        trend = "No revenue data available"
    
    return JsonResponse({
        'categories': category_names,
        'revenue': category_revenue,
        'trend': trend
    })

def dashboard_tickets(request):
    """API endpoint for ticket availability for upcoming events"""
    # Get upcoming events
    today = timezone.now().date()
    upcoming_events = Event_management.objects.filter(
        start_date__gte=today
    ).order_by('start_date')[:5]  # Get top 5 upcoming events
    
    events = []
    available_tickets = []
    sold_tickets = []
    
    for event in upcoming_events:
        events.append(event.title)
        available_tickets.append(event.available_tickets)
        
        # Calculate sold tickets based on payments
        sold = Payment.objects.filter(
            event=event,
            payment_status='PAID'
        ).count()
        
        sold_tickets.append(sold)
    
    # Calculate trend
    nearly_sold_out = sum(1 for avail, sold in zip(available_tickets, sold_tickets) 
                         if avail > 0 and sold / (avail + sold) >= 0.8)
    
    trend = f"{nearly_sold_out} events nearly sold out"
    
    return JsonResponse({
        'events': events,
        'available_tickets': available_tickets,
        'sold_tickets': sold_tickets,
        'trend': trend
    })

def dashboard_categories(request):
    """API endpoint for events by category"""
    # Get event count by category
    categories_data = Category.objects.annotate(
        event_count=Count('event_management')
    ).values('name', 'event_count')
    
    categories = [
        {'name': cat['name'], 'count': cat['event_count']} 
        for cat in categories_data
    ]
    
    # Find largest category
    if categories:
        largest_category = max(categories, key=lambda x: x['count'])
        trend = f"{largest_category['name']} is the largest category"
    else:
        trend = "No category data available"
    
    return JsonResponse({
        'categories': categories,
        'trend': trend
    })

#payment
def add_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('display_payment')
    else:
        form = PaymentForm()

    return render(request, 'paymentform.html', {'form': form, 'title': 'Add Payment'})

def display_payment(request):
    payments = Payment.objects.all()
    return render(request, 'display_payment.html', {'payments': payments})

#updating 

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth
import json

from .models import (
    Event_management,
    Speaker_management,
    Participant_management,
    Schedule_management,
    Payment
)

def dashboard(request):
    # Get date filters from request or use defaults
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else timezone.now().date() - timedelta(days=30)
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
    except ValueError:
        start_date = timezone.now().date() - timedelta(days=30)
        end_date = timezone.now().date()
    
    # Get summary statistics
    total_events = Event_management.objects.filter(start_date__gte=start_date, end_date__lte=end_date).count()
    total_participants = Participant_management.objects.count()
    
    # Calculate total revenue from payments
    revenue_result = Payment.objects.filter(
        payment_date__gte=start_date,
        payment_date__lte=end_date,
        payment_status='PAID'
    ).aggregate(total=Sum('amount_paid'))
    total_revenue = revenue_result['total'] or 0
    
    # Calculate total available tickets
    tickets_result = Event_management.objects.filter(
        start_date__gte=start_date
    ).aggregate(total=Sum('available_tickets'))
    total_tickets = tickets_result['total'] or 0
    
    # Get upcoming events
    upcoming_events = Event_management.objects.filter(
        start_date__gte=timezone.now().date()
    ).order_by('start_date')[:5]
    
    # Get recent payments
    recent_payments = Payment.objects.all().order_by('-payment_date')[:5]
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_events': total_events,
        'total_participants': total_participants,
        'total_revenue': total_revenue,
        'total_tickets': total_tickets,
        'upcoming_events': upcoming_events,
        'recent_payments': recent_payments,
    }
    
    return render(request, 'dashboard/index.html', context)

def api_category_distribution(request):
    # Get date filters from request
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else timezone.now().date() - timedelta(days=30)
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
    except ValueError:
        start_date = timezone.now().date() - timedelta(days=30)
        end_date = timezone.now().date()
    
    # Get event counts by category
    events_by_category = Event_management.objects.filter(
        start_date__gte=start_date,
        end_date__lte=end_date
    ).values('category__name').annotate(count=Count('id')).order_by('-count')
    
    # Calculate percentages
    total_events = sum(item['count'] for item in events_by_category)
    
    if total_events > 0:
        labels = [item['category__name'] for item in events_by_category]
        values = [round((item['count'] / total_events) * 100) for item in events_by_category]
    else:
        labels = []
        values = []
    
    return JsonResponse({
        'labels': labels,
        'values': values
    })

def api_revenue_trend(request):
    # Get date filters from request
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else timezone.now().date() - timedelta(days=180)
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
    except ValueError:
        start_date = timezone.now().date() - timedelta(days=180)
        end_date = timezone.now().date()
    
    # Get monthly revenue
    monthly_revenue = Payment.objects.filter(
        payment_date__gte=start_date,
        payment_date__lte=end_date,
        payment_status='PAID'
    ).annotate(
        month=TruncMonth('payment_date')
    ).values('month').annotate(
        total=Sum('amount_paid')
    ).order_by('month')
    
    labels = [item['month'].strftime('%b') for item in monthly_revenue]
    values = [float(item['total']) for item in monthly_revenue]
    
    return JsonResponse({
        'labels': labels,
        'values': values
    })

def api_payment_methods(request):
    # Get date filters from request
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else timezone.now().date() - timedelta(days=30)
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
    except ValueError:
        start_date = timezone.now().date() - timedelta(days=30)
        end_date = timezone.now().date()
    
    # Get payment counts by method
    payments_by_method = Payment.objects.filter(
        payment_date__gte=start_date,
        payment_date__lte=end_date
    ).values('payment_method').annotate(count=Count('id')).order_by('-count')
    
    # Calculate percentages
    total_payments = sum(item['count'] for item in payments_by_method)
    
    if total_payments > 0:
        labels = [dict(Payment.PAYMENT_METHOD_CHOICES).get(item['payment_method']) for item in payments_by_method]
        values = [round((item['count'] / total_payments) * 100) for item in payments_by_method]
    else:
        labels = []
        values = []
    
    return JsonResponse({
        'labels': labels,
        'values': values
    })


#testing payment
def create_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('payment_list')  # or to a success page
    else:
        form = PaymentForm()
    return render(request, 'payment_form.html', {'form': form})


def payment_list(request):
    payments = Payment.objects.select_related('participant', 'event').all()
    return render(request, 'payment_list.html', {'payments': payments})

def paid_events(request):
    paid_events = Event_management.objects.filter(event_charge__gt=0)

    return render(request,'paid_events.html',{'paid_events': paid_events})

def paid_events_view(request):
    # Events that are not free and have price > 0
    paid_events = Event_management.objects.filter(is_free=False, price__gt=0)
    return render(request, 'paid_events.html', {'events': paid_events})
def free_events_view(request):
    # Events marked as free and price = 0
    free_events = Event_management.objects.filter(is_free=True, price=0)
    return render(request, 'free_events.html', {'events': free_events})