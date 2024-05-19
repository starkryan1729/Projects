import streamlit as st
from event import Event
from make_calendar import Calendar
from datetime import datetime, timezone
from utils import to_time_ns
from django.utils.timezone import make_aware

e1 = Event(90 * 60 * 1e9, "Make Dinner")
e2 = Event(20 * 60 * 1e9, "Yoga")
e3 = Event(30 * 60 * 1e9, "Eat Dinner")
e4 = Event(45 * 60 * 1e9, "Do Dishes")
e5 = Event(10 * 60 * 1e9, "Do Laundry")
calendar = Calendar("US/Pacific")
# start_time = calendar.timezone.localize(datetime(year=2024, month=5, day=13, hour=15))
# calendar.add_event(event=e1, start_time_ns=to_time_ns(start_time))
# start_time2 = calendar.timezone.localize(datetime(year=2024, month=5, day=13, hour=17))
# calendar.add_event(event=e2, start_time_ns=to_time_ns(start_time2))
calendar.schedule_events_asap([e1, e2, e3, e4, e5])
calendar.check_for_conflicts()
calendar.display()
start_busy_time = calendar.timezone.localize(datetime(year=2024, month=5, day=19, hour=12, minute=1))
end_busy_time = calendar.timezone.localize(datetime(year=2024, month=5, day=19, hour=14, minute=2))
st.write(f"Busy from {start_busy_time} to {end_busy_time}.")
calendar.set_block_to_busy(to_time_ns(start_busy_time), to_time_ns(end_busy_time))
calendar.check_for_conflicts()
calendar.display()
