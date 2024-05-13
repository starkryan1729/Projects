import datetime
from utils import Frequency

class Event():
    def __init__(self, duration_time_ns: int, name: str, recurring: bool = False, recur_freq: Frequency = Frequency.WEEKLY):
        self.duration_time_ns = duration_time_ns
        self.name = name
        self.recurring = recurring
        self.recur_freq = recur_freq
    
    @staticmethod
    def get_duration_ns(event) -> int:
        return event.duration_time_ns

    def to_str(self) -> str:
        return f"{self.name} for {self.duration_time_ns / 1e9 / 60} minutes"
