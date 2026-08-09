
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

"""
from analyze import get_consistency_score
session = get_session(2022, 'Mexico', 'R')
score = get_consistency_score(session, 'VER')
print(score)"""


"""
from fetch import get_session, get_driver_laps
session = get_session(2026, 'Austria', 'R')
laps = get_driver_laps(session, 'VER')
print(laps['Stint'].unique())
"""



"""
from fetch import get_session, get_driver_laps
session = get_session(2025, 'Spain', 'R')
laps = get_driver_laps(session, 'VER')
laps=laps.copy()
laps['LapTimeSeconds']=laps['LapTime'].dt.total_seconds()
print("after laptimeseconds", len(laps))
print("num of stints", laps['Stint'].unique())
for stint in laps['Stint'].unique():
    stint_laps=laps[laps['Stint']==stint]
    print(f"stint {stint}: {len(stint_laps)} laps")
    flying_laps = stint_laps[
        stint_laps['PitInTime'].isna()&
        stint_laps['PitOutTime'].isna()]
    print(f" flying laps: {len(flying_laps)}")"""





"""
from fetch import get_session
from charts import chart_consistency
session = get_session(2025, 'Abu Dhabi', 'R')
fig = chart_consistency(session, ['VER', 'NOR'])
fig.show()
"""                    


"""
from fetch import get_session
from charts import chart_head_to_head
session = get_session(2022, 'Mexico', 'R')
fig = chart_head_to_head(session, 'VER', 'LEC')
fig.show()"""




"""
from fetch import get_session
from charts import chart_position_change
session = get_session(2021, 'Abu Dhabi', 'R')
fig = chart_position_change(session, ['VER', 'LEC', 'HAM', 'STR', 'RIC', 'VET', 'RAI'])
fig.show()
"""

"""
from fetch import get_session
from charts import chart_quali_comparison
session = get_session(2026, 'Japan', 'Q')
fig = chart_quali_comparison(session, 'HAD', 'VER')
fig.show()
"""

"""
from fetch import get_session
session= get_session(2026,'Monaco', 'Q')
laps = session.laps.pick_drivers('VER')
best_lap = laps.pick_fastest()
telemetry = best_lap.get_telemetry()
print(telemetry.columns.tolist())
print(telemetry.head())
"""


"""
from fetch import get_session
import numpy as np
from analyze import get_telemetry_for_lap, interpolate_telemetry
session = get_session(2026, 'Belgium', 'Q')
laps = session.laps.pick_drivers('VER')
best_lap = laps.pick_fastest()
telemetry = get_telemetry_for_lap(best_lap)
max_distance = telemetry['Distance'].max()
distance_grid = np.arange(0, max_distance, 10)
interpolated = interpolate_telemetry(telemetry, distance_grid)
print(f"original telem points {len(telemetry)}")
print(f"interp points: {len(interpolated)}")
"""


"""
from fetch import get_session
session = get_session(2023, 'Monaco', 'Q')
laps = session.laps.pick_drivers('VER')
best_lap = laps.pick_fastest()
telemetry = best_lap.get_telemetry()
print(telemetry.columns.tolist())"""




"""
from fetch import get_session
from analyze import detect_mistakes
from charts import chart_track_mistakes
session = get_session(2026, 'Belgium', 'Q')
mistakes = detect_mistakes(session, 'STR')
result = chart_track_mistakes(session, 'STR')
print(result)
"""



"""
from fetch import get_session
from charts import chart_perfect_lap
session = get_session(2024, 'Baku', 'Q')
fig = chart_perfect_lap(session, 'VER')
fig.show()
"""
