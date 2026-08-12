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

"""
from fetch import get_session
from charts import chart_quali_improvement
session = get_session(2018, 'Qatar', 'Q')
fig = chart_quali_improvement(session, ['PER', 'VER', 'ALO', 'HAM'])
fig.show()
"""      


"""
from fetch import get_session
from analyze import get_circuit_dna
session1 = get_session(2025, 'Hungary', 'Q')
dna1 = get_circuit_dna(session1)
session2 = get_session(2026, 'Hungary', 'Q')
dna2 = get_circuit_dna(session2)
print(f"full throttle:  {dna1['throttle_pct']}% vs {dna2['throttle_pct']}%")
print(f"braking:{dna1['braking_pct']}% vs {dna2['braking_pct']}%")
print(f"top speed:{dna1['top_speed']} vs {dna2['top_speed']} km/h")
print(f"avg corner speed: {dna1['avg_corner_speed']} vs {dna2['avg_corner_speed']} km/h")
print(f"low speed corners:{dna1['low_speed_pct']}% vs {dna2['low_speed_pct']}%")
print(f"high speed: {dna1['high_speed_pct']}% vs {dna2['high_speed_pct']}%")
"""


"""
from fetch import get_session
from charts import chart_circuit_dna
session1 =get_session(2026, 'Silverstone', 'Q')
session2 =get_session(2026, 'Monaco', 'Q')
fig = chart_circuit_dna([session1, session2])
fig.show()
""" 

"""
from fetch import get_session
from analyze import get_circuit_dna, classify_circuit
circuits = [
    ('Hungarian Grand Prix', 'Hungary'),
    ('Monaco Grand Prix', 'Monaco'),
    ('Barcelona Grand Prix', 'Barcelona'),]
for event, name in circuits:
    try:
        session = get_session(2022, event, 'FP1')
        dna = get_circuit_dna(session)
        result = classify_circuit(dna)
        print(f"{name}: {result['label']} (throttle:{dna['throttle_pct']}% corner:{dna['avg_corner_speed']}km/h low:{dna['low_speed_pct']}%)")
    except Exception as e:
        print(f"{name}: Error - {e}")
        """


"""
from fetch import get_session
from analyze import get_team_circuit_affinity
from charts import chart_team_circuit_affinity
sessions= {
    'High Speed': [
        get_session(2021, 'British Grand Prix', 'Q'),
        get_session(2021, 'Japanese Grand Prix', 'Q'),],
    'High Downforce': [
        get_session(2023, 'Monaco Grand Prix', 'Q'),
        get_session(2023, 'Hungarian Grand Prix', 'Q'),],
    'Balanced': [
        get_session(2025, 'Canadian Grand Prix', 'Q'),
        get_session(2025, 'Barcelona Grand Prix', 'Q'),]}
results = get_team_circuit_affinity(sessions)
fig = chart_team_circuit_affinity(results)
fig.show()
"""


"""
from fetch import get_session
from analyze import get_driver_circuit_affinity
sessions = {
    'High Speed': [
        get_session(2023, 'British Grand Prix', 'Q'),
        get_session(2023, 'Japanese Grand Prix', 'Q'),   ],
    'High Downforce': [
        get_session(2023, 'Monaco Grand Prix', 'Q'),
        get_session(2023, 'Miami Grand Prix', 'Q'),],
    'Balanced': [
        get_session(2023, 'Canadian Grand Prix', 'Q'),
        get_session(2023, 'Barcelona Grand Prix', 'Q'),]}
results = get_driver_circuit_affinity(sessions)
for circuit_type, drivers in results.items():
    print(f"\n{circuit_type} — Top 5:")
    for driver, avg_pos in list(drivers.items())[:5]:
        print(f"  {driver}: P{avg_pos}")
    """




"""
from fetch import get_session
from analyze import get_driver_circuit_affinity
from charts import chart_driver_circuit_affinity
sessions = {
    'High Speed': [
        get_session(2026, 'British Grand Prix', 'Q'),
        get_session(2026, 'Japanese Grand Prix', 'Q'),],
    'High Downforce': [
        get_session(2026, 'Monaco Grand Prix', 'Q'),
        get_session(2026, 'Miami Grand Prix', 'Q'),],
    'Balanced': [
        get_session(2026, 'Canadian Grand Prix', 'Q'),
        get_session(2026, 'Barcelona Grand Prix', 'Q'),]}
results = get_driver_circuit_affinity(sessions)
ref_session = get_session(2026, 'British Grand Prix', 'Q')
fig = chart_driver_circuit_affinity(results, ref_session)
fig.show() 
"""









"""
from fetch import get_session
from analyze import get_weather
from charts import chart_weather
wet_sessions = [
    get_session(2024, 'Monaco', 'Q'),
    get_session(2023, 'Netherlands', 'Q'), ]
dry_sessions = [
    get_session(2023, 'British Grand Prix', 'Q'),
    get_session(2023, 'Saudi Arabin Grand Prix', 'Q'),
    get_session(2023, 'Japanese Grand Prix', 'Q'), ]
drivers = ['VER', 'HAM', 'LEC', 'NOR', 'RUS']
results= get_weather(wet_sessions, dry_sessions, drivers)
ref_session = get_session(2026, 'British Grand Prix', 'Q')
fig = chart_weather(results, ref_session)
fig.show()
"""


"""
from fetch import get_session
from analyze import get_tire_degradation
from charts import chart_tire_degradation
session = get_session(2026, 'Hungarian Grand Prix', 'R')
data = get_tire_degradation(session, 'VER')
for stint, info in data.items():
    print(f"Stint {stint} - {info['compound']}: {info['deg_rate']}s/lap deg")
fig = chart_tire_degradation(session, 'VER')
fig.show()
"""




"""
from analyze import get_teammate_gap
from charts import chart_teammate_gap
events = [ 
    'Australian Grand Prix',
    'Chinese Grand Prix',
    'Japanese Grand Prix',
    'Miami Grand Prix',
    'Canadian Grand Prix',
    'Monaco Grand Prix',
    'Barcelona Grand Prix',
    'British Grand Prix',
    'Belgium Grand Prix',
    'Hungarian Grand Prix',]
sessions = []
for event in events:
    try:
        s = get_session(2018, event, 'Q')
        sessions.append(s)
    except:
        continue
data = get_teammate_gap(2018, sessions, 'SAI', 'VER')
for race in data['races']:
    print(f"{race['event']}: {race['gap']}s {race['faster']}faster")
fig = chart_teammate_gap(data)
fig.show()
"""




"""
from analyze import get_fastest_lap_history
from charts import chart_fastest_lap_history
history = get_fastest_lap_history(
    'Monaco Grand Prix',
    [2018,2019,2020,2021,2022,2023,2024,2025,2026])
for h in history['history']:
    print(f"{h['year']}: {h['lap_time']}s {h['driver']}")
fig = chart_fastest_lap_history(history)
fig.show()"""


"""
from analyze import get_driver_circuit_stats
from charts import chart_driver_circuit_stats
stats = get_driver_circuit_stats(
    'VER',
    'Brazilian Grand Prix',
    [2018,2019,2020,2021,2022,2023,2024,2025])
ref_session = get_session(2025, 'Brazilian Grand Prix', 'Q')
fig = chart_driver_circuit_stats(stats, ref_session)
fig.show()
"""