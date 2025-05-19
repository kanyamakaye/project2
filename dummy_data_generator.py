import os
from django.core.wsgi import get_wsgi_application
settings_path = 'event_project.settings'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_path)
application = get_wsgi_application()

from django.contrib.auth.models import User
from event_app.models import Category ,Event_management, Speaker_management, Participant_management, Schedule_management, Payment

from faker import Faker # type: ignore
import random
import json
from datetime import date

fake = Faker()



# Create categories
categories = ['Conference', 'Workshop', 'Seminar', 'Webinar', 'Meetup']

for category_name in categories:
    Category.objects.create(name=category_name)

# Create events
events = []

for _ in range(100):
    title = fake.catch_phrase()
    description = fake.paragraph()
    start_date = fake.date_between(start_date=start_date)
    end_date = fake.date_between(end_date=end_date)
    location = fake.address()
    category = random.choice(Category.objects.all())
    is_free = random.choice([True, False])
    
    event = Event_management.objects.create(
        title=title,
        description=description,
        start_date=start_date,
        end_date=end_date,
        location=location,
        category=category,
        is_free=is_free
    )
    events.append(event)

# Create speakers
speakers = []

for _ in range(100):
    name = fake.name()
    biography = fake.paragraph()
    email = fake.email()
    phone_number = fake.phone_number()
    linkedin_link = fake.url()
    twitter_link = fake.url()
    
    speaker = Speaker_management.objects.create(
        name=name,
        biography=biography,
        email=email,
        phone_number=phone_number,
        linkedin_link=linkedin_link,
        twitter_link=twitter_link
    )
    speakers.append(speaker)

# Create participants
participants = []

for _ in range(100):
    name = fake.name()
    email = fake.email()
    phone_number = fake.phone_number()
    
    participant = Participant_management.objects.create(
        name=name,
        email=email,
        phone_number=phone_number
    )
    participants.append(participant)

# Create schedules
schedules = []

for event in events:
    for _ in range(random.randint(1, 5)):
        start_time = fake.date_time_between(start_date=event.start_date, end_date=event.end_date)
        end_time = fake.date_time_between(start_date=start_time, end_date=event.end_date)
        topic = fake.catch_phrase()
        speaker = random.choice(speakers)
        
        schedule = Schedule_management.objects.create(
            event=event,
            start_time=start_time,
            end_time=end_time,
            topic=topic,
            speaker=speaker
        )
        schedules.append(schedule)

# Create payments
payments = []

for participant in participants:
    for _ in range(random.randint(1, 5)):
        event = random.choice(events)
        amount_paid = random.uniform(10, 1000)
        payment_method = random.choice(['Credit Card', 'PayPal', 'Bank Transfer'])
        payment_date = fake.date_between(start_date=event.start_date, end_date=event.end_date)
        transaction_id = fake.uuid4()
        payment_status = random.choice(['PAID', 'PENDING', 'FAILED'])
        
        payment = Payment.objects.create(
            participant=participant,
            event=event,
            amount_paid=amount_paid,
            payment_method=payment_method,
            payment_date=payment_date,
            transaction_id=transaction_id,
            payment_status=payment_status
        )
        payments.append(payment)

# Serialize the populated data to a JSON file
data = {
    'events': list(Event_management.objects.values()),
    'speakers': list(Speaker_management.objects.values()),
    'participants': list(Participant_management.objects.values()),
    'schedules': list(Schedule_management.objects.values()),
    'payments': list(Payment.objects.values())
}

with open('event_management_data.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)
