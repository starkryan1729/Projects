import streamlit as st
from event import Event
from make_calendar import Calendar
from datetime import datetime, timezone
from utils import to_time_ns
from django.utils.timezone import make_aware



e1 = Event(90 * 60 * 1e9, "Make dinner")
e2 = Event(20 * 60 * 1e9, "Do yoga")
e3 = Event(30 * 60 * 1e9, "Eat dinner")
e4 = Event(45 * 60 * 1e9, "Do dishes")
e5 = Event(10 * 60 * 1e9, "Do laundry")
e6 = Event(20 * 60 * 1e9, "Eat lunch")
calendar = Calendar("US/Pacific")

# get these from an LLM API call, probably
calendar.schedule_events_smart(order_matters = {
            "Eat lunch": 12,
            "Make dinner": -1,
            "Eat dinner": 18,
            "Do dishes": -1
        },
        order_does_not_matter = ["Do yoga", "Do laundry"],
        events = {
            "Make dinner": e1,
            "Do yoga": e2,
            "Eat dinner": e3,
            "Do dishes": e4,
            "Do laundry": e5,
            "Eat lunch": e6
        })
calendar.check_for_conflicts()
calendar.display()

# currently hard-coded for demo; in app, all UI will be drag-based
start_busy_time = calendar.timezone.localize(datetime(year=2024, month=5, day=19, hour=12, minute=1))
end_busy_time = calendar.timezone.localize(datetime(year=2024, month=5, day=19, hour=14, minute=2))
st.write(f"Busy from {start_busy_time} to {end_busy_time}.")
calendar.set_block_to_busy(to_time_ns(start_busy_time), to_time_ns(end_busy_time))
calendar.check_for_conflicts()
calendar.display()

start_not_busy_time = calendar.timezone.localize(datetime(year=2024, month=5, day=19, hour=13, minute=10))
end_not_busy_time = calendar.timezone.localize(datetime(year=2024, month=5, day=19, hour=13, minute=45))
st.write(f"Not busy from {start_not_busy_time} to {end_not_busy_time}.")
calendar.set_block_to_not_busy(to_time_ns(start_not_busy_time), to_time_ns(end_not_busy_time))
calendar.check_for_conflicts()
calendar.display()
