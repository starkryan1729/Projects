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
    
    def schedule_events_asap(self, events: List[Event]):
        events.sort(key=Event.get_duration_ns)
        for event in events:
            self.schedule_event_asap(event)
    
    def set_block_to_busy(self, start_time, end_time):
        events_to_reschedule = {}
        for event_start_time in self.events:
            event = self.events[event_start_time]
            event_end_time = event_start_time + event.duration_time_ns
            if start_time <= event_start_time <= end_time or start_time <= event_end_time <= end_time or (event_start_time <= start_time and end_time <= event_end_time):
                events_to_reschedule[event_start_time] = event
        for event_start_time in events_to_reschedule:
            self.events.pop(event_start_time)
        busy_event = Event(end_time - start_time, "Busy")
        self.schedule_event(busy_event, start_time, rounding=False)
        self.schedule_events_asap(list(events_to_reschedule.values()))
    
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
