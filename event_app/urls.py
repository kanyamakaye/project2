from django.urls import path
from . import views
from .models import Participant_management, Payment, Schedule_management
from django.utils import timezone

urlpatterns = [
    # Home and Core URLs
    path('', views.home, name='home'),
    path('event-count/', views.event_count, name='event_count'),
    
    # Event Management URLs
    path('events/', views.events_list, name='events_list'),
    path('events/all/', views.event_details, name='event_list'),
    path('event/<str:event_title>/', views.event_details, name='event_details'),
    path('event-form/', views.event_forms, name='event_forms'),
    path('upcoming/', views.upcoming, name='upcoming'),
    
    # Speaker Management URLs
    path('speakers/', views.speaker_list, name='speaker_list'),
    path('speaker/<int:id>/', views.details_of_speaker, name='speaker_details'),
    path('speaker-form/', views.speaker_forms, name='speaker_forms'),
    
    # Participant Management URLs
    path('participants/', views.participant_list, name='participant_list'),
    path('participant-form/', views.participant_forms, name='participant_forms'),
    path('participant/edit/<int:participant_id>/', views.edit_participant, name='edit_participant'),
    path('participant/delete/<int:participant_id>/', views.delete_participant, name='delete_participant'),
    path('participants/categories/', views.participant_categories, name='participant_categories'),
    path('participants/category/<int:category_id>/', views.participants_by_category, name='participants_by_category'),
    path('participants/with-payments/', views.participants_with_all_payments, name='participants_with_all_payments'),
    path('participants/top-paying/', views.top_paying_participants, name='top_paying_participants'),
    path('participants/recent/', views.recent_payers, name='recent_payers'),
    
    # Analytics URLs
    #working
    path('analytics/average-price/', views.average_price_analytics, name='average_price_analytics'),
    path('analytics/participant-stats/', views.participant_statistics, name='participant_statistics'),
    path('analytics/event-stats/', views.event_statistics, name='event_statistics'),
    path('analytics/top-revenue/', views.top_revenue_events, name='top_revenue_events'),
    path('analytics/highest-paid/', views.highest_paid_events, name='highest_paid_events'),
    
    # Schedule and Categories URLs
    path('schedule/', views.display_schedule, name='display_schedule'),
   # path('schedule/forms',views.schedule_forms),
    path('make_schedule/',views.schedule_forms),
    path('make_category/',views.cat_forms),
    path('categories/', views.categories, name='categories'),
    path('schedule/forms/', views.schedule_forms, name='schedule_forms'),
    
    # Profile and Settings URLs
    path('profile/', views.profile, name='profile'),
    # Admin URLs - Updated to use the correct view functions
    path('events/', views.admin_events, name='admin_events'),
    path('free-events/', views.admin_free_events, name='admin_free_events'),
    path('paid-events/', views.admin_paid_events, name='admin_paid_events'),
    path('participants/', views.admin_participants, name='admin_participants'),
    path('speakers/', views.admin_speakers, name='admin_speakers'),
    path('categories/', views.admin_categories, name='admin_categories'),
    path('schedule/', views.admin_schedule, name='admin_schedule'),
    path('payments/', views.admin_payments, name='admin_payments'),
    
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    #sample to test 
    path('api/dashboard/summary/', views.dashboard_summary, name='dashboard_summary'),#working
    path('api/dashboard/registrations/', views.dashboard_registrations, name='dashboard_registrations'),#working
    path('api/dashboard/revenue/', views.dashboard_revenue, name='dashboard_revenue'),#working
    path('api/dashboard/tickets/', views.dashboard_tickets, name='dashboard_tickets'),#working
    path('api/dashboard/categories/', views.dashboard_categories, name='dashboard_categories'),#working
    path('dashboard/',views.admin_dashboard),

    #payments
    path('add-payment/', views.add_payment, name='add_payment'),
    path('payments/', views.display_payment, name='display_payment'),# not working 
    path('testing/',views.dashboard_summary),

    #demo
    path('cat/form',views.cat_forms),
    path('categories/',views.categories),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/dashboard/category-distribution/', views.api_category_distribution, name='api_category_distribution'),
    path('api/dashboard/revenue-trend/', views.api_revenue_trend, name='api_revenue_trend'),
    path('api/dashboard/payment-methods/', views.api_payment_methods, name='api_payment_methods'),
    
    #testing payment
    path('payment/', views.create_payment, name='create_payment'),
    path('payments/', views.payment_list, name='payment_list'),

    #free event testing 
     path('events/paid/', views.paid_events_view, name='paid_events'),
     path('events/free/', views.free_events_view, name='free_events'),
]
