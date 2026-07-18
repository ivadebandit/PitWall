"""
from fetch import get_session
from analyze import get_race_pace, get_head_to_head, get_consistency_score
"""
"""

session = get_session(2023, 'Australia', 'R')
print("--- VER Race Pace by Stint ---")
pace = get_race_pace(session, 'VER')
print(pace)


print("\n--- VER Consistency Score ---")
score = get_consistency_score(session, 'VER')
print(score)


print("\n--- VER vs GAS Head to Head---")
h2h = get_head_to_head(session, 'VER', 'ANT')
print(h2h[['LapNumber', 'LapTimeSeconds', 'Driver']].head(15))
"""

"""
session = get_session(2023, 'Australia', 'R')
print(session.laps[['Driver', 'DriverNumber']].drop_duplicates())
"""
"""
from fetch import get_session
from analyze import get_h2h_summary
session = get_session(2026, 'Australia', 'R')
print("--- VER vs LEC Overall H2H ---")
summary = get_h2h_summary(session, 'VER', 'HAD')
print(summary)
print(f"Driver 1 avg: {summary['driver1']}s")
print(f"Driver 2 avg: {summary['driver2']}s")
print(f"Gap: {summary['gap']}s")
print(f"Faster driver: {summary['faster_driver']}")
"""

"""
from fetch import get_session
from charts import get_driver_color

session = get_session(2023, 'Singapore', 'R')

color_ver = get_driver_color(session, 'VER')
color_lec = get_driver_color(session, 'LEC')

print(f"VER color: {color_ver}")
print(f"LEC color: {color_lec}")
"""

"""
from fetch import get_session
from charts import chart_race_pace

session = get_session(2025, 'Spain', 'R')

fig = chart_race_pace(session, 'VER')
fig.show()
"""

"""
from fetch import get_session
from charts import chart_head_to_head
session = get_session(2022, 'Mexico', 'R')
fig = chart_head_to_head(session, 'VER', 'HAM')
fig.show()
"""

"""
from fetch import get_session
from charts import chart_consistency
session = get_session(2026, 'Austria', 'R')

fig = chart_consistency(session, ['VER', 'RUS', 'ANT', 'HAM', 'LEC', 'HAD'])
fig.show()
"""

"""
from fetch import get_session
from charts import chart_quali_comparison
session = get_session(2026, 'Monaco', 'Q')
fig = chart_quali_comparison(session, 'VER', 'ANT')
fig.show()
"""
"""
from fetch import get_session
from charts import chart_position_change

session = get_session(2026, 'Austria', 'R')

fig = chart_position_change(session, ['VER', 'HAD', 'HAM', 'LEC', 'NOR', 'PIA', 'ANT', 'RUS'])
fig.show()
"""
"""
from fetch import get_session
session = get_session(2026, 'Monaco', 'R')
print(session.laps[['Driver', 'DriverNumber']].drop_duplicates())
"""

"""
from fetch import get_session
from charts import chart_position_change, chart_consistency
session = get_session(2024, 'Brazil', 'R')
fig1 = chart_position_change(session, ['VER', 'NOR'])
fig1.show()
"""

"""
from fetch import get_session

session = get_session(2026, 'Monaco', 'Q')
laps = session.laps.pick_drivers('VER')

best_lap = laps.pick_fastest()
telemetry = best_lap.get_telemetry()
print(telemetry.columns.tolist())
print(telemetry.head())
"""

"""
from fetch import get_session

session = get_session(2023, 'Australia', 'Q')
laps = session.laps.pick_drivers('VER')
best_lap = laps.pick_fastest()
telemetry = best_lap.get_telemetry()
print(telemetry[['Distance', 'Speed', 'Throttle', 'Brake', 'nGear']].head(10))
"""

"""
from fetch import get_session
import numpy as np
from analyze import get_telemetry_for_lap, interpolate_telemetry

session = get_session(2024, 'Monaco', 'Q')
laps = session.laps.pick_drivers('VER')

best_lap = laps.pick_fastest()

telemetry = get_telemetry_for_lap(best_lap)

max_distance = telemetry['Distance'].max()
distance_grid = np.arange(0, max_distance, 10)

interpolated = interpolate_telemetry(telemetry, distance_grid)

print(f"Original telemetry points: {len(telemetry)}")
print(f"Interpolated points: {len(interpolated)}")
print(interpolated.head(10))
"""

"""
from fetch import get_session
from analyze import detect_mistakes
session = get_session(2026, 'British Grand Prix', 'Q')
mistakes = detect_mistakes(session, 'NOR')
print(f"Found {len(mistakes)} mistakes\n")
for i, mistake in enumerate(mistakes):
    print(f"Mistake {i+1}:")
    print(f"  Location: {mistake['distance_start']}m to {mistake['distance_end']}m")
    print(f"  Worst point: {mistake['worst_point']}m")
    print(f"  Speed loss: {mistake['max_speed_loss']} km/h")
    print(f"  Time lost: {mistake['time_lost']}s")
    print()
"""

"""
from fetch import get_session

session = get_session(2026, 'British Grand Prix', 'Q')

circuit_info = session.get_circuit_info()
print(circuit_info.corners)
"""
"""
from fetch import get_session
from analyze import detect_mistakes

session = get_session(2026, 'British Grand Prix', 'Q')

mistakes = detect_mistakes(session, 'NOR')

print(f"Found {len(mistakes)} mistakes\n")
for i, mistake in enumerate(mistakes):
    print(f"Mistake {i+1} — Turn {mistake['turn_number']}:")
    print(f"  Location: {mistake['distance_start']}m to {mistake['distance_end']}m")
    print(f"  Speed loss: {mistake['max_speed_loss']} km/h")
    print(f"  Time lost: {mistake['time_lost']}s")
    print()
"""

"""
from fetch import get_session
from charts import chart_track_mistakes

session = get_session(2026, 'British Grand Prix', 'Q')

chart_track_mistakes(session, 'NOR')
"""

"""
from fetch import get_session
from charts import chart_race_pace, chart_head_to_head, chart_consistency, chart_position_change

session = get_session(2026, 'British Grand Prix', 'R')

fig1 = chart_race_pace(session, 'NOR')
fig1.show()

fig2 = chart_head_to_head(session, 'NOR', 'PIA')
fig2.show()

fig3 = chart_consistency(session, ['NOR', 'PIA', 'VER', 'HAD'])
fig3.show()

fig4 = chart_position_change(session, ['NOR', 'PIA', 'VER', 'HAD'])
fig4.show()
"""

"""
from fetch import get_session
from charts import chart_race_pace, chart_head_to_head, chart_consistency, chart_position_change
session = get_session(2026, 'British Grand Prix', 'R')
fig1 = chart_race_pace(session, 'NOR')
fig1.show()
"""

"""
from fetch import get_session
from analyze import get_perfect_lap

session = get_session(2025, 'Abu Dhabi', 'Q')

result = get_perfect_lap(session, 'VER')


print(f"Best S1: {result['best_s1']}s (Lap {result['best_s1_lap']})")
print(f"Best S2: {result['best_s2']}s (Lap {result['best_s2_lap']})")
print(f"Best S3: {result['best_s3']}s (Lap {result['best_s3_lap']})")
print(f"Perfect lap: {result['perfect_time']}s")
print(f"Best actual: {result['best_actual']}s")
print(f"Time gain: {result['time_gain']}s")
"""

"""
from fetch import get_session
from charts import chart_perfect_lap
session = get_session(2025, 'Abu Dhabi', 'Q')
fig = chart_perfect_lap(session, 'LEC')
fig.show()
"""

"""
from fetch import get_session
from charts import chart_track_mistakes

session = get_session(2026, 'British Grand Prix', 'Q')
chart_track_mistakes(session, 'NOR')
"""

"""
from fetch import get_session
from analyze import get_quali_improvement

session = get_session(2026, 'British Grand Prix', 'Q')
result = get_quali_improvement(session, 'NOR')
print(f"Q1 best: {result['times']['Q1']}s")
print(f"Q2 best: {result['times']['Q2']}s")
print(f"Q3 best: {result['times']['Q3']}s")
print(f"Q1 to Q2 improvement: {result['improvements']['Q1_to_Q2']}s")
print(f"Q2 to Q3 improvement: {result['improvements']['Q2_to_Q3']}s")
print(f"Q1 to Q3 total improvement: {result['improvements']['Q1_to_Q3']}s")
"""


"""
from fetch import get_session
session = get_session(2026, 'British Grand Prix', 'Q')
laps = session.laps.pick_drivers('NOR')
print(laps.columns.tolist())
"""






"""
from fetch import get_session
session = get_session(2026, 'British Grand Prix', 'Q')
print(session.results[['Abbreviation', 'Q1', 'Q2', 'Q3']])
"""



"""
from fetch import get_session
from charts import chart_quali_improvement
session = get_session(2026, 'British Grand Prix', 'Q')
fig = chart_quali_improvement(session, ['NOR', 'VER', 'LEC', 'HAM', 'ANT'])
fig.show()
""" 
  

"""
from fetch import get_session
from analyze import get_circuit_dna
session = get_session(2026, 'British Grand Prix', 'Q')
dna = get_circuit_dna(session)

print(f"Circuit: {dna['circuit']} {dna['year']}")
print(f"Full throttle: {dna['throttle_pct']}%")
print(f"Braking: {dna['braking_pct']}%")
print(f"Top speed: {dna['top_speed']} km/h")
print(f"Avg corner speed: {dna['avg_corner_speed']} km/h")
print(f"Low speed corners: {dna['low_speed_pct']}%")
print(f"High speed cornering: {dna['high_speed_pct']}%")
"""



"""
from fetch import get_session
from analyze import get_circuit_dna

session1 = get_session(2026, 'British Grand Prix', 'Q')
dna1 = get_circuit_dna(session1)
session2 = get_session(2026, 'Monaco Grand Prix', 'Q')
dna2 = get_circuit_dna(session2)

print("SILVERSTONE vs MONACO")
print(f"Full throttle:      {dna1['throttle_pct']}% vs {dna2['throttle_pct']}%")
print(f"Braking:            {dna1['braking_pct']}% vs {dna2['braking_pct']}%")
print(f"Top speed:          {dna1['top_speed']} vs {dna2['top_speed']} km/h")
print(f"Avg corner speed:   {dna1['avg_corner_speed']} vs {dna2['avg_corner_speed']} km/h")
print(f"Low speed corners:  {dna1['low_speed_pct']}% vs {dna2['low_speed_pct']}%")
print(f"High speed:         {dna1['high_speed_pct']}% vs {dna2['high_speed_pct']}%")
"""



"""
from fetch import get_session
from charts import chart_circuit_dna
session = get_session(2026, 'British Grand Prix', 'Q')

fig = chart_circuit_dna(session)
fig.show()
"""

"""

from fetch import get_session
from charts import chart_circuit_dna
session1 = get_session(2026, 'British Grand Prix', 'Q')
session2 = get_session(2026, 'Monaco Grand Prix', 'Q')
fig = chart_circuit_dna([session1, session2])
fig.show()
"""

"""
from fetch import get_session
from analyze import get_circuit_dna, classify_circuit

session1 = get_session(2026, 'British Grand Prix', 'Q')
session2 = get_session(2026, 'Monaco Grand Prix', 'Q')
dna1 = get_circuit_dna(session1)
dna2 = get_circuit_dna(session2)
result1 = classify_circuit(dna1)
result2 = classify_circuit(dna2)
print(f"{result1['circuit']}: {result1['label']}")
print(f"  {result1['description']}")
print()
print(f"{result2['circuit']}: {result2['label']}")
print(f"  {result2['description']}") """

"""
from fetch import get_session
from analyze import get_circuit_dna, classify_circuit

circuits = [
    ('British Grand Prix', 'Silverstone'),
    ('Monaco Grand Prix', 'Monaco'),
    ('Italian Grand Prix', 'Monza'),
    ('Japanese Grand Prix', 'Suzuka'),
    ('Canadian Grand Prix', 'Montreal'),]
for event, name in circuits:
    session = get_session(2026, event, 'Q')
    dna = get_circuit_dna(session)
    result = classify_circuit(dna)
    print(f"{name}: {result['label']}") """


"""
from fetch import get_session
from analyze import get_circuit_dna, classify_circuit
session = get_session(2026, 'Italian Grand Prix', 'Q')
dna = get_circuit_dna(session)
result = classify_circuit(dna)
print(f"Monza: {result['label']}") """



"""
from fetch import get_session
from analyze import get_circuit_dna, classify_circuit
"""
"""
circuits = [
    ('British Grand Prix', 'Silverstone'),
    ('Monaco Grand Prix', 'Monaco'),
    ('Canadian Grand Prix', 'Montreal'),
    ('Australian Grand Prix', 'Melbourne'),
    ('Japanese Grand Prix', 'Suzuka'),
]

for event, name in circuits:
    try:
        session = get_session(2026, event, 'Q')
        dna = get_circuit_dna(session)
        result = classify_circuit(dna)
        print(f"{name}: {result['label']}")
    except Exception as e:
        print(f"{name}: Error - {e}")
        """


"""
session = get_session(2026, 'Japanese Grand Prix', 'Q')
dna = get_circuit_dna(session)
print(dna)"""

"""

from fetch import get_session
from analyze import get_circuit_dna, classify_circuit

circuits = [
    ('British Grand Prix', 'Silverstone'),
    ('Monaco Grand Prix', 'Monaco'),
    ('Canadian Grand Prix', 'Montreal'),
    ('Australian Grand Prix', 'Melbourne'),
    ('Japanese Grand Prix', 'Suzuka'),
    ('Miami Grand Prix', 'Miami'),
    ('Barcelona Grand Prix', 'Barcelona'),
]

for event, name in circuits:
    try:
        session = get_session(2026, event, 'Q')
        dna = get_circuit_dna(session)
        result = classify_circuit(dna)
        print(f"{name}: {result['label']} (throttle:{dna['throttle_pct']}% corner:{dna['avg_corner_speed']}km/h low:{dna['low_speed_pct']}%)")
    except Exception as e:
        print(f"{name}: Error - {e}")   """


"""
from fetch import get_session
from analyze import get_circuit_dna, classify_circuit

circuits = [
    ('British Grand Prix', 'Silverstone'),
    ('Monaco Grand Prix', 'Monaco'),
    ('Canadian Grand Prix', 'Montreal'),
    ('Australian Grand Prix', 'Melbourne'),
    ('Japanese Grand Prix', 'Suzuka'),
    ('Miami Grand Prix', 'Miami'),
    ('Barcelona Grand Prix', 'Barcelona'),
]

for event, name in circuits:
    try:
        session = get_session(2026, event, 'Q')
        dna = get_circuit_dna(session)
        result = classify_circuit(dna)
        print(f"{name}: {result['label']}")
    except Exception as e:
        print(f"{name}: Error - {e}")
        """


"""

from fetch import get_session
from analyze import get_circuit_dna, classify_circuit, get_team_circuit_affinity

sessions = {
    'High Speed': [
        get_session(2026, 'British Grand Prix', 'Q'),
        get_session(2026, 'Japanese Grand Prix', 'Q'),
    ],
    'High Downforce': [
        get_session(2026, 'Monaco Grand Prix', 'Q'),
        get_session(2026, 'Miami Grand Prix', 'Q'),
    ],
    'Balanced': [
        get_session(2026, 'Canadian Grand Prix', 'Q'),
        get_session(2026, 'Barcelona Grand Prix', 'Q'),
    ]
}

results = get_team_circuit_affinity(sessions)

for circuit_type, teams in results.items():
    print(f"\n{circuit_type}:")
    for team, avg_pos in list(teams.items())[:5]:
        print(f"  {team}: P{avg_pos}")
"""



"""

from fetch import get_session
from analyze import get_team_circuit_affinity
from charts import chart_team_circuit_affinity

sessions = {
    'High Speed': [
        get_session(2026, 'British Grand Prix', 'Q'),
        get_session(2026, 'Japanese Grand Prix', 'Q'),
    ],
    'High Downforce': [
        get_session(2026, 'Monaco Grand Prix', 'Q'),
        get_session(2026, 'Miami Grand Prix', 'Q'),
    ],
    'Balanced': [
        get_session(2026, 'Canadian Grand Prix', 'Q'),
        get_session(2026, 'Barcelona Grand Prix', 'Q'),
    ]
}

results = get_team_circuit_affinity(sessions)
fig = chart_team_circuit_affinity(results)
fig.show()
"""



"""
from fetch import get_session
from analyze import get_driver_circuit_affinity

sessions = {
    'High Speed': [
        get_session(2026, 'British Grand Prix', 'Q'),
        get_session(2026, 'Japanese Grand Prix', 'Q'),   ],
    'High Downforce': [
        get_session(2026, 'Monaco Grand Prix', 'Q'),
        get_session(2026, 'Miami Grand Prix', 'Q'),
      ],
    'Balanced': [
        get_session(2026, 'Canadian Grand Prix', 'Q'),
        get_session(2026, 'Barcelona Grand Prix', 'Q'),
    ]
}

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
        get_session(2026, 'Japanese Grand Prix', 'Q'),
    ],
    'High Downforce': [
        get_session(2026, 'Monaco Grand Prix', 'Q'),
        get_session(2026, 'Miami Grand Prix', 'Q'),
    ],
    'Balanced': [
        get_session(2026, 'Canadian Grand Prix', 'Q'),
        get_session(2026, 'Barcelona Grand Prix', 'Q'),
    ]
}

results = get_driver_circuit_affinity(sessions)
ref_session = get_session(2026, 'British Grand Prix', 'Q')

fig = chart_driver_circuit_affinity(results, ref_session)
fig.show()        """






"""

from fetch import get_session
from analyze import get_weather
from charts import chart_weather
wet_sessions = [
    get_session(2024, 'Monaco', 'Q'),
    get_session(2023, 'Netherlands', 'Q'), ]

dry_sessions = [
    get_session(2026, 'British Grand Prix', 'Q'),
    get_session(2026, 'Monaco Grand Prix', 'Q'),
    get_session(2026, 'Japanese Grand Prix', 'Q'),
]

drivers = ['VER', 'HAM', 'LEC', 'NOR', 'RUS']
results = get_weather(wet_sessions, dry_sessions, drivers)
for driver, data in results.items():
    print(f"{driver}: Wet P{data['wet_avg']} | Dry P{data['dry_avg']} | Wet advantage: {data['wet_advantage']}")

ref_session = get_session(2026, 'British Grand Prix', 'Q')
fig = chart_weather(results, ref_session)
fig.show()
 """



"""
from fetch import get_session
from analyze import get_tire_degradation
from charts import chart_tire_degradation

session = get_session(2026, 'British Grand Prix', 'R')

data = get_tire_degradation(session, 'VER')
for stint, info in data.items():
    print(f"Stint {stint} - {info['compound']}: {info['deg_rate']}s/lap degradation")

fig = chart_tire_degradation(session, 'VER')
fig.show()"""


"""
from fetch import get_session
from analyze import get_teammate_gap
from charts import chart_teammate_gap
events = [
    'Australian Grand Prix',
    'Chinese Grand Prix',
    'Japanese Grand Prix',
    'Miami Grand Prix',
    'Canadian Grand Prix',
    'Monaco Grand Prix',
    'Barcelona Grand Prix',]

sessions = []
for event in events:
    try:
        s = get_session(2026, event, 'Q')
        sessions.append(s)
    except:
        continue
data = get_teammate_gap(2026, sessions, 'VER', 'HAD')
for race in data['races']:
    print(f"{race['event']}: {race['gap']}s — {race['faster']} faster")

fig = chart_teammate_gap(data)
fig.show()  

"""

              
"""
from analyze import get_fastest_lap_history
from charts import chart_fastest_lap_history

history = get_fastest_lap_history(
    'British Grand Prix',
    [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
)
for h in history['history']:
    print(f"{h['year']}: {h['lap_time']}s — {h['driver']}")

fig = chart_fastest_lap_history(history)
fig.show() 
"""  

"""

from analyze import get_driver_circuit_stats
from charts import chart_driver_circuit_stats
from fetch import get_session
stats = get_driver_circuit_stats(
    'VER',
    'British Grand Prix',
    [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
)


for h in stats['history']:
    print(f"{h['year']}: Quali P{h['quali_pos']} | Race P{h['race_pos']} | Status: {h['status']}")

ref_session = get_session(2026, 'British Grand Prix', 'Q')
fig = chart_driver_circuit_stats(stats, ref_session)
fig.show()

"""
    





from fetch import get_session
from analyze import get_sector_improvement, get_pitstop_performance
from charts import chart_sector_improvement, chart_pitstop_performance

session_r = get_session(2026, 'British Grand Prix', 'R')

sector_data = get_sector_improvement(session_r, 'NOR')
for stint, data in sector_data.items():
    print(f"Stint {stint} - {data['compound']}: {len(data['tyre_life'])} laps")

fig1 = chart_sector_improvement(sector_data, 'NOR')
fig1.show()

pitstops = get_pitstop_performance(session_r)
for p in pitstops[:5]:
    print(f"{p['driver']} Lap {p['lap']}: {p['duration']}s")

fig2 = chart_pitstop_performance(pitstops, session_r)
fig2.show()
 
  
   
"""
from fetch import get_session
from analyze import get_sector_improvement, get_pitstop_performance
from charts import chart_sector_improvement, chart_pitstop_performance
session_r = get_session(2026, 'British Grand Prix', 'R')
pitstops = get_pitstop_performance(session_r)
print(f"Found {len(pitstops)} pit stops")
for p in pitstops[:5]:
    print(p)
"""