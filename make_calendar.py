from utils import to_time_ns
from datetime import datetime, timezone
from event import Event
from pytz import timezone as pytz_timezone

class Calendar():
    def __init__(self, timezone: str):
        self.timezone: str = pytz_timezone(timezone)
        self.events: dict[int, Event] = None
    
    def add_event(self, event: Event, start_time_ns: int):
        if self.events is None:
            self.events = {}
        self.events[start_time_ns] = event
        self.events = dict(sorted(self.events.items()))
    
    def check_for_conflicts(self) -> bool:
        start_times = list(self.events.keys())
        for i in range(len(start_times) - 1):
            if start_times[i + 1] < start_times[i] + self.events[start_times[i]].duration_time_ns:
                return False
        return True
    
    def display_str(self) -> str:
        display_str = ""
        for key, value in self.events.items():
            display_str = display_str + f"At {datetime.fromtimestamp(key / 1e9)}, {value.to_str()} \n"
        return display_str
