from utils import to_time_ns
from datetime import datetime, timezone
from event import Event
from pytz import timezone as pytz_timezone
import streamlit as st
from typing import List

class Calendar():
    def __init__(self, timezone: str, increment_ns: int = 5 * 60 * 1e9):
        self.timezone = pytz_timezone(timezone)
        self.events: dict[int, Event] = None
        self.increment_ns = increment_ns
        self.order_matters: dict[str, int] = {}
        self.order_does_not_matter: List[str] = []
    
    def schedule_events_smart(self, order_matters: dict[str, int], order_does_not_matter: List[str], events: dict[str, Event]):
        """
        THIS QUERY to ChatGPT returns the order_matters and order_doesnt_matter data structures. API call will be added later.
        Of the events: do dishes, do yoga, make dinner, eat dinner, do laundry, eat lunch, which ones matter for order
        Can you return the events where order matters as a Python dictionary, and the events where order doesn't matter as a separate Python list? Do not include anything else in the formatting.
        For the Python dictionary, if there is a suggested start hour for the event, include it as the value in the dictionary. Otherwise, the value can be -1.

        ChatGPT-4o returns:
        order_matters = {
            "Eat lunch": 12,
            "Make dinner": -1,
            "Eat dinner": 18,
            "Do dishes": -1
        }
        order_does_not_matter = ["Do yoga", "Do laundry"]
        """
        self.order_matters = order_matters
        self.order_does_not_matter = order_does_not_matter

        now = datetime.now(tz=self.timezone)
        last_time_ns = to_time_ns(now)
        for event_name in self.order_matters:
            if event_name in events:
                if self.order_matters[event_name] >= 0:
                    desired_start_time_ns = to_time_ns(self.timezone.localize(datetime(year=now.year, month=now.month, day=now.day, hour=self.order_matters[event_name])))
                    last_time_ns = desired_start_time_ns
                    self.schedule_event(events[event_name], desired_start_time_ns)
                else:
                    self.schedule_event(events[event_name], last_time_ns)
        
        order_does_not_matter_events = [events[event_name] for event_name in events if event_name in self.order_does_not_matter]
        self.schedule_events_asap(order_does_not_matter_events)

    
    def schedule_events_asap(self, events: List[Event]):
        events.sort(key=Event.get_duration_ns)
        for event in events:
            self.schedule_event_asap(event)
    
    def set_block_to_not_busy(self, start_time, end_time):
        events_to_remove = {}
        events_to_add = {}
        events_to_reschedule = []
        for event_start_time in self.events:
            event = self.events[event_start_time]
            if event.name == "Busy":
                event_end_time = event_start_time + event.duration_time_ns
                if start_time <= event_start_time <= end_time:
                    events_to_remove[event_start_time] = event
                    if end_time < event_end_time:
                        busy_event = Event(event_end_time - end_time, "Busy")
                        events_to_add[end_time] = busy_event
                elif start_time <= event_end_time <= end_time:
                    events_to_remove[event_start_time] = event
                    if event_start_time < start_time:
                        busy_event = Event(start_time - event_start_time, "Busy")
                        events_to_add[event_start_time] = busy_event
                elif event_start_time <= start_time and end_time <= event_end_time:
                    events_to_remove[event_start_time] = event
                    busy_event1 = Event(start_time - event_start_time, "Busy")
                    events_to_add[event_start_time] = busy_event1
                    busy_event2 = Event(event_end_time - end_time, "Busy")
                    events_to_add[end_time] = busy_event2
            elif event_start_time >= end_time:
                events_to_remove[event_start_time] = event
                events_to_reschedule.append(event)
        for event_start_time in events_to_remove:
            self.events.pop(event_start_time)
        for event_start_time in events_to_add:
            event = events_to_add[event_start_time]
            self.schedule_event(event, event_start_time, rounding=False)
        events_to_reschedule_by_name = {}
        for event in events_to_reschedule:
            events_to_reschedule_by_name[event.name] = event
        self.schedule_events_smart(self.order_matters, self.order_does_not_matter, events_to_reschedule_by_name)

    
    def set_block_to_busy(self, start_time, end_time):
        events_to_reschedule: dict[str, Event] = {}
        for event_start_time in self.events:
            event = self.events[event_start_time]
            event_end_time = event_start_time + event.duration_time_ns
            if start_time <= event_start_time <= end_time or start_time <= event_end_time <= end_time or (event_start_time <= start_time and end_time <= event_end_time):
                events_to_reschedule[event_start_time] = event
        new_end_time = end_time
        for event_start_time in events_to_reschedule:
            self.events.pop(event_start_time)
        for event_start_time in events_to_reschedule:
            event = events_to_reschedule[event_start_time]
            if event.name in self.order_matters and self.order_matters[event.name] >= 0:
                new_end_time += event.duration_time_ns
        for event_start_time in self.events:
            event = self.events[event_start_time]
            event_end_time = event_start_time + event.duration_time_ns
            if end_time <= event_start_time <= new_end_time or end_time <= event_end_time <= new_end_time or (event_start_time <= end_time and new_end_time <= event_end_time):
                events_to_reschedule[event_start_time] = event
        busy_event = Event(end_time - start_time, "Busy")
        self.schedule_event(busy_event, start_time, rounding=False)
        events_to_reschedule_by_name = {}
        for event_start_time in events_to_reschedule:
            event = events_to_reschedule[event_start_time]
            events_to_reschedule_by_name[event.name] = event
        self.schedule_events_smart(self.order_matters, self.order_does_not_matter, events_to_reschedule_by_name)
    
    def schedule_event_asap(self, event: Event):
        self.schedule_event(event, to_time_ns(datetime.now(tz=self.timezone)))
    
    def schedule_event(self, event: Event, desired_start_ns: int, rounding: bool = True):
        if rounding:
            desired_ns_rounded_up = int((desired_start_ns // self.increment_ns) * self.increment_ns)
            if desired_start_ns % self.increment_ns != 0:
                desired_ns_rounded_up += self.increment_ns
        else:
            desired_ns_rounded_up = desired_start_ns
        num_increments = int((event.duration_time_ns // self.increment_ns) + 1)
        done_search = False
        begin_time_ns = desired_ns_rounded_up
        while(not done_search):
            time_ns = begin_time_ns
            might_work = True
            for i in range(num_increments):
                if self.has_event(time_ns):
                    might_work = False
                    break
                time_ns += self.increment_ns
            if might_work:
                done_search = True
            else:
                begin_time_ns = time_ns + self.increment_ns
        self.add_event(event, begin_time_ns)
    
    def add_event(self, event: Event, start_time_ns: int):
        if self.events is None:
            self.events = {}
        self.events[start_time_ns] = event
        self.events = dict(sorted(self.events.items()))
    
    def has_event(self, time_ns: int) -> bool:
        if self.events is None:
            return False
        for time, event in self.events.items():
            if time > time_ns:
                break
            if time_ns < time + event.duration_time_ns:
                return True
        return False
    
    def check_for_conflicts(self) -> bool:
        start_times = list(self.events.keys())
        for i in range(len(start_times) - 1):
            if start_times[i + 1] < start_times[i] + self.events[start_times[i]].duration_time_ns:
                st.write(f"Oh no! Conflict found between {self.events[start_times[i]].to_str()} and {self.events[start_times[i + 1]].to_str()}!")
                return False
        st.write("No conflicts!")
        return True
    
    def display(self) -> str:
        for key, value in self.events.items():
            st.write(f"At {datetime.fromtimestamp(key / 1e9)}, {value.to_str()}")
