from fetch import get_session
"""

from fetch import get_session
from analyze import get_race_pace, get_h2h
session = get_session(2026, 'Hungary', 'R')
print("--- VER Race Pace by Stint ---")
pace = get_race_pace(session, 'VER')
print(pace)

"""
"""

from fetch import get_session
from charts import get_driver_color


session = get_session(2018, 'Australia', 'R')
color_ver = get_driver_color(session, 'VER')
color_alo = get_driver_color(session, 'ALO')
color_vet = get_driver_color(session, 'VET')
print(color_ver)
print(color_alo)
print(color_vet)"""


from analyze import get_consistency_score
session = get_session(2022, 'Mexico', 'R')
score = get_consistency_score(session, 'VER')
print(score)