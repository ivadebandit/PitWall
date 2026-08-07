
from fetch import get_session
from analyze import get_race_pace, get_h2h
session = get_session(2026, 'Hungary', 'R')
print("--- VER Race Pace by Stint ---")
pace = get_race_pace(session, 'VER')
print(pace)