import streamlit as st
from event import Event
from make_calendar import Calendar
from datetime import datetime, timezone
from utils import to_time_ns
from django.utils.timezone import make_aware

e1 = Event(30 * 60 * 1e9, "Make Dinner")
e2 = Event(90 * 60 * 1e9, "Yoga")
calendar = Calendar("US/Pacific")
start_time = calendar.timezone.localize(datetime(year=2024, month=4, day=1, hour=17))
calendar.add_event(event=e1, start_time_ns=to_time_ns(start_time))
start_time2 = calendar.timezone.localize(datetime(year=2024, month=4, day=1, hour=11))
calendar.add_event(event=e2, start_time_ns=to_time_ns(start_time2))
calendar.schedule_event_asap(e1)
calendar.schedule_event_asap(e2)
calendar.check_for_conflicts()
calendar.display()
