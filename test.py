import os
import fastf1


os.makedirs('fastf1_cache', exist_ok=True)
fastf1.Cache.enable_cache('fastf1_cache')
print("testing")
session = fastf1.get_session(2026, 'Hungary', 'Q')
session.load(telemetry=False, weather=False)
fastest_lap = session.laps.pick_fastest()
print(f"pole: {fastest_lap['Driver']} with a time of {fastest_lap['LapTime']}")