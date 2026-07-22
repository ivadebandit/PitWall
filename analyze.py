import pandas as pd
import numpy as np
from fetch import get_session, get_driver_laps




def get_clean_laps(session, driver):
    laps = get_driver_laps(session, driver)
    laps = laps[laps['IsAccurate'] == True]
    laps = laps[laps['Deleted'] == False]
    laps = laps[laps['TrackStatus'] == '1']
    laps = laps.dropna(subset=['LapTime'])

    return laps





def get_race_pace(session, driver):
    laps = get_clean_laps(session, driver)
    laps = laps.copy()
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()
    pace = laps.groupby('Stint').agg(
        AvgLapTime=('LapTimeSeconds', 'mean'),
        Compound=('Compound', 'first'),
        Lapcount=('LapNumber', 'count')
    ).reset_index()
    return pace




def get_head_to_head(session, driver1, driver2):
    
    
    
    laps1 = get_clean_laps(session, driver1)
    laps2 = get_clean_laps(session, driver2)

    laps1 = laps1.copy()
    laps2 = laps2.copy()
    
    laps1['LapTimeSeconds'] = laps1['LapTime'].dt.total_seconds()
    laps2['LapTimeSeconds'] = laps2['LapTime'].dt.total_seconds()

    laps1['Driver'] = driver1
    laps2['Driver'] = driver2

    combined = pd.concat([laps1, laps2])

    return combined




def get_consistency_score(session, driver):
    
    
    laps = get_clean_laps(session, driver)

    laps = laps.copy()
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()

    score = laps['LapTimeSeconds'].std()

    return round(score, 3)





def get_h2h_summary(session, driver1, driver2):
    
    
    
    laps1 = get_clean_laps(session, driver1)
    laps2 = get_clean_laps(session, driver2)
    laps1 = laps1.copy()
    laps2 = laps2.copy()
    laps1['LapTimeSeconds'] = laps1['LapTime'].dt.total_seconds()
    laps2['LapTimeSeconds'] = laps2['LapTime'].dt.total_seconds()
    avg1 = laps1['LapTimeSeconds'].mean()
    avg2 = laps2['LapTimeSeconds'].mean()

    diff = abs(avg1 - avg2)

    faster = driver1 if avg1 < avg2 else driver2

    summary = {
        'driver1': round(avg1, 3),
        'driver2': round(avg2, 3),
        'gap': round(diff, 3),
        'faster_driver': faster
    }
    
    return summary






def get_quali_laps(session, driver):
  
    laps = get_driver_laps(session, driver)

    laps = laps.copy()
    laps['S1'] = laps['Sector1Time'].dt.total_seconds()
    laps['S2'] = laps['Sector2Time'].dt.total_seconds()
    laps['S3'] = laps['Sector3Time'].dt.total_seconds()
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()

    laps = laps.dropna(subset=['S1', 'S2', 'S3'])

    best_lap = laps.loc[laps['LapTimeSeconds'].idxmin()]

    return best_lap    




def get_position_change(session, driver):



    laps = get_driver_laps(session, driver)
    laps = laps.copy()

    position_data = laps[['LapNumber', 'Position']].dropna()

    driver_info = session.get_driver(driver)
    grid_position = driver_info['GridPosition']

    start_row = pd.DataFrame({
        'LapNumber': [0],
        'Position': [grid_position]
    })

    position_data = pd.concat([start_row, position_data]).reset_index(drop=True)
    
    return position_data


import numpy as np
from scipy import interpolate


def get_telemetry_for_lap(lap):
    



    telemetry = lap.get_telemetry()

    telemetry = telemetry[['Distance', 'Speed', 'Throttle', 'Brake', 'nGear']].copy()

    telemetry = telemetry.dropna()

    return telemetry



def interpolate_telemetry(telemetry, distance_grid):
   
   

    speed_interp = interpolate.interp1d(
        telemetry['Distance'],
        telemetry['Speed'],
        kind='linear',
        fill_value='extrapolate'
    )

    throttle_interp = interpolate.interp1d(
        telemetry['Distance'],
        telemetry['Throttle'],
        kind='linear',
        fill_value="extrapolate"
    )

    brake_interp = interpolate.interp1d(
        telemetry['Distance'],
        telemetry['Brake'].astype(float),
        kind='linear',
        fill_value='extrapolate'
    )

    gear_interp = interpolate.interp1d(
        telemetry['Distance'],
        telemetry['nGear'],
        kind='linear',
        fill_value='extrapolate'
    )

    
    result = pd.DataFrame({
        'Distance': distance_grid,
        'Speed': speed_interp(distance_grid),
        'Throttle': throttle_interp(distance_grid),
        'Brake': brake_interp(distance_grid),
        'nGear': gear_interp(distance_grid)
    })

    return result

def get_corner_for_distance(circuit_info, distance):
 
    corners = circuit_info.corners

    corners = corners.copy()
    corners['diff'] = abs(corners['Distance'] - distance)
    nearest = corners.loc[corners['diff'].idxmin()]

    turn_number = int(nearest['Number'])
    corner_distance = round(nearest['Distance'], 1)
    return turn_number, corner_distance




def detect_mistakes(session, driver, lap_number=None):
   


    laps = session.laps.pick_drivers(driver)

    best_lap = laps.pick_fastest()

    if lap_number is None:
        sorted_laps = laps.sort_values('LapTime').dropna(subset=['LapTime'])
        if len(sorted_laps) < 2:
            return []
        comparison_lap = sorted_laps.iloc[1]
    else:
        comparison_lap = laps[laps['LapNumber'] == lap_number].iloc[0]

    best_telemetry = get_telemetry_for_lap(best_lap)
    comp_telemetry = get_telemetry_for_lap(comparison_lap)

    max_distance = min(
        best_telemetry['Distance'].max(),
        comp_telemetry['Distance'].max()
    )
    distance_grid = np.arange(0, max_distance, 10)

    best_interp = interpolate_telemetry(best_telemetry, distance_grid)
    comp_interp = interpolate_telemetry(comp_telemetry, distance_grid)

    speed_diff = comp_interp['Speed'] - best_interp['Speed']

    mistake_threshold = -5.0
    mistake_mask = speed_diff < mistake_threshold

    mistakes = []
    in_mistake = False
    mistake_start = None
    mistake_start_idx = None

    circuit_info = session.get_circuit_info()
    for i, (is_mistake, distance) in enumerate(zip(mistake_mask, distance_grid)):
        if is_mistake and not in_mistake:
            in_mistake = True
            mistake_start = distance
            mistake_start_idx = i

        elif not is_mistake and in_mistake:
            in_mistake = False
            mistake_end = distance

            zone_diff = speed_diff.iloc[mistake_start_idx:i]
            worst_speed_loss = zone_diff.min()
            worst_distance = distance_grid[mistake_start_idx + zone_diff.argmin()]

            zone_length = mistake_end - mistake_start
            avg_speed_loss = abs(zone_diff.mean())

            avg_best_speed = best_interp['Speed'].iloc[mistake_start_idx:i].mean()
            avg_comp_speed = comp_interp['Speed'].iloc[mistake_start_idx:i].mean()

            if avg_comp_speed > 0 and avg_best_speed > 0:
                time_best = zone_length / (avg_best_speed / 3.6)
                time_comp = zone_length / (avg_comp_speed / 3.6)
                time_lost = round(time_comp - time_best, 3)
            else:
                time_lost = 0

            if time_lost > 0.05:
                turn_number, corner_dist = get_corner_for_distance(
                    circuit_info,
                    worst_distance
                )
                mistakes.append({
                    'distance_start': round(mistake_start, 1),
                    'distance_end': round(mistake_end, 1),
                    'worst_point': round(worst_distance, 1),
                    'max_speed_loss': round(abs(worst_speed_loss), 1),
                    'time_lost': time_lost,
                    'turn_number': turn_number,
                    'corner_distance': corner_dist
                })

    mistakes.sort(key=lambda x: x['time_lost'], reverse=True)

    return mistakes

    
def get_perfect_lap(session, driver):
  


    laps = get_driver_laps(session, driver)
    laps = laps.copy()

    laps['S1'] = laps['Sector1Time'].dt.total_seconds()
    laps['S2'] = laps['Sector2Time'].dt.total_seconds()
    laps['S3'] = laps['Sector3Time'].dt.total_seconds()
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()

    laps = laps.dropna(subset=['S1', 'S2', 'S3'])

    best_s1 = laps['S1'].min()
    best_s2 = laps['S2'].min()
    best_s3 = laps['S3'].min()

    best_s1_lap = laps.loc[laps['S1'].idxmin(), 'LapNumber']
    best_s2_lap = laps.loc[laps['S2'].idxmin(), 'LapNumber']
    best_s3_lap = laps.loc[laps['S3'].idxmin(), 'LapNumber']

    perfect_time = best_s1 + best_s2 + best_s3

    best_actual = laps['LapTimeSeconds'].min()

    time_gain = round(best_actual - perfect_time, 3)

    return {
        'best_s1': round(best_s1, 3),
        'best_s2': round(best_s2, 3),
        'best_s3': round(best_s3, 3),
        'best_s1_lap': int(best_s1_lap),
        'best_s2_lap': int(best_s2_lap),
        'best_s3_lap': int(best_s3_lap),
        'perfect_time': round(perfect_time, 3),
        'best_actual': round(best_actual, 3),
        'time_gain': time_gain
    }




def get_quali_improvement(session, driver):
    

    driver_results = session.results[session.results['Abbreviation'] == driver]

    if driver_results.empty:
        return None
    row = driver_results.iloc[0]

    def to_seconds(val):
        if pd.isna(val):
            return None
        return round(val.total_seconds(), 3)
    q1 = to_seconds(row['Q1'])
    q2 = to_seconds(row['Q2'])
    q3 = to_seconds(row['Q3'])
    results = {'Q1': q1, 'Q2': q2, 'Q3': q3}

    improvements = {}
    if q1 and q2:
        improvements['Q1_to_Q2'] = round(q1 - q2, 3)
    else:
        improvements['Q1_to_Q2'] = None
    if q2 and q3:
        improvements['Q2_to_Q3'] = round(q2 - q3, 3)
    else:
        improvements['Q2_to_Q3'] = None
    if q1 and q3:
        improvements['Q1_to_Q3'] = round(q1 - q3, 3)
    else:
        improvements['Q1_to_Q3'] = None
    return {'times': results,
        'improvements': improvements,
        'driver': driver }








def get_circuit_dna(session):
    fastest_lap = session.laps.pick_fastest()
    telemetry = fastest_lap.get_telemetry()

   
    full_throttle = (telemetry['Throttle'] == 100).sum() # high power circuit if full throttle is used many times throughout a lap
    total_points = len(telemetry)
    throttle_pct = round((full_throttle / total_points) * 100, 1)

    braking = (telemetry['Brake'] == True).sum() # how much braking is required during a lap
    braking_pct = round((braking / total_points) * 100, 1)

    top_speed = round(telemetry['Speed'].max(), 1) # maximum top speed

    cornering = telemetry[
        (telemetry['Throttle'] < 100) &
        (telemetry['Brake'] == False) # avg corner speed, tells if most corners are fast/slow 
    ]
    if len(cornering) > 0:
        avg_corner_speed = round(cornering['Speed'].mean(), 1)
    else:
        avg_corner_speed = 0

    low_speed = (telemetry['Speed'] < 120).sum() # low speed corners percentage (below 120kmh)
    low_speed_pct = round((low_speed / total_points) * 100, 1) # if its high its it mainly has slow corners

    high_speed_cornering = telemetry[ # its a high df cicuit if it hsa many fast/high speed corners
        (telemetry['Speed'] > 200) &
        (telemetry['Throttle'] < 100)
    ]
    high_speed_pct = round((len(high_speed_cornering) / total_points) * 100, 1)

    return {
        'throttle_pct': throttle_pct,
        'braking_pct': braking_pct,
        'top_speed': top_speed,
        'avg_corner_speed': avg_corner_speed,
        'low_speed_pct': low_speed_pct,
        'high_speed_pct': high_speed_pct,
        'circuit': session.event['EventName']  }




def classify_circuit(dna):
    throttle = dna['throttle_pct']
    braking = dna['braking_pct']
    corner_speed = dna['avg_corner_speed']
    low_speed = dna['low_speed_pct']
    top_speed = dna['top_speed']
    high_speed = dna['high_speed_pct']

    if corner_speed > 160 and high_speed > 10:
        label = "High Speed"
        description = "Fast flowing corners require aero efficiency and driver commitment."
    elif throttle > 60 and top_speed > 315:
        label = "Power Track"
        description = "Long straights and high top speeds. Low drag setups and raw engine power are needed."
    elif low_speed > 15:
        label = "High Downforce"
        description = "Tight corners and heavy braking require max downforce and mechanical grip."
    elif braking > 25 and corner_speed < 160:
        label = "Stop/Go"
        description = "Many hard braking zones followed by slow corners. Brakes and traction matter the most."
    else:
        label = "Balanced"
        description = "No single characteristic dominates. A well rounded setup is needed."
    return {
        'label': label,
        'description': description,
        'circuit': dna['circuit'] }
                              



def get_team_circuit_affinity(sessions_by_type):
    results = {}

    for circuit_type, sessions in sessions_by_type.items():
        team_positions = {}
        for session in sessions:
            quali_results = session.results[['Abbreviation', 'TeamName', 'Position']]
            for _, row in quali_results.iterrows():
                team = row['TeamName']
                position = row['Position']
                if pd.isna(position) or pd.isna(team):
                    continue

                if team not in team_positions:
                    team_positions[team] = []
                team_positions[team].append(float(position))

        team_avg = {}
        for team, positions in team_positions.items():
            team_avg[team] = round(sum(positions) / len(positions), 2)
        results[circuit_type] = dict(
            sorted(team_avg.items(), key=lambda x: x[1]) )

    return results




def get_driver_circuit_affinity(sessions_by_type):
    results = {}

    for circuit_type, sessions in sessions_by_type.items():
        driver_positions = {}
        for session in sessions:
            quali_results = session.results[['Abbreviation', 'Position']]
            for _, row in quali_results.iterrows():
                driver = row['Abbreviation']
                position = row['Position']
                if pd.isna(position) or pd.isna(driver):
                    continue
                if driver not in driver_positions:
                    driver_positions[driver] = []
                driver_positions[driver].append(float(position))

        driver_avg = {}
        for driver, positions in driver_positions.items():
            driver_avg[driver] = round(sum(positions) / len(positions), 2)
        results[circuit_type] = dict(
            sorted(driver_avg.items(), key=lambda x: x[1])
         )

    return results









def get_weather(sessions_wet, sessions_dry, drivers):
    def avg_position(sessions, driver):
        positions = []
        for session in sessions:
            try:
                driver_row = session.results[
                    session.results['Abbreviation'] == driver ]
                if not driver_row.empty:
                    pos = driver_row.iloc[0]['Position']
                    if not pd.isna(pos):
                        positions.append(float(pos))
            except:
                continue
        if positions:
            return round(sum(positions) / len(positions), 2)
        return None

    results = {}
    for driver in drivers:
        wet_avg = avg_position(sessions_wet, driver)
        dry_avg = avg_position(sessions_dry, driver)

        if wet_avg and dry_avg:
            wet_advantage = round(dry_avg - wet_avg, 2)
        else:
            wet_advantage = None
        results[driver] = {
            'wet_avg': wet_avg,
            'dry_avg': dry_avg,
            'wet_advantage': wet_advantage    }
    return results     
          




def get_tire_degradation(session, driver):



    laps = get_driver_laps(session, driver)
    laps = laps.copy()
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()
    laps = laps.dropna(subset=['LapTimeSeconds', 'TyreLife', 'Stint'])

    results = {}
    for stint in laps['Stint'].unique():
        stint_laps = laps[laps['Stint'] == stint].copy()
        if len(stint_laps) < 3:
            continue
        compound = stint_laps['Compound'].iloc[0]
        stint_laps = stint_laps[
            stint_laps['PitInTime'].isna() &
            stint_laps['PitOutTime'].isna()  ]
        stint_laps = stint_laps[stint_laps['TrackStatus'] == '1']
        stint_laps = stint_laps[stint_laps['TyreLife'] > 2]
        stint_laps = stint_laps[stint_laps['IsAccurate'] == True]
        if len(stint_laps) < 3:
            continue

        tyre_life = stint_laps['TyreLife'].values
        lap_times = stint_laps['LapTimeSeconds'].values

        if len(tyre_life) > 1:
            deg_rate = round(
                (lap_times[-1] - lap_times[0]) / (tyre_life[-1] - tyre_life[0]),
                3)
        else:
            deg_rate = 0
        results[int(stint)] = {
            'compound': compound,
            'tyre_life': tyre_life.tolist(),
            'lap_times': lap_times.tolist(),
            'deg_rate': deg_rate
             }
    return results
  




def get_teammate_gap(year, team_sessions, driver1, driver2):



    results = []
    for session in team_sessions:
        try:
            d1_row = session.results[session.results['Abbreviation'] == driver1]
            d2_row = session.results[session.results['Abbreviation'] == driver2]
            if d1_row.empty or d2_row.empty:
                continue
            def get_best_time(row):
                for col in ['Q3', 'Q2', 'Q1']:
                    val = row.iloc[0][col]
                    if not pd.isna(val):
                        return val.total_seconds()
                return None
            t1 = get_best_time(d1_row)
            t2 = get_best_time(d2_row)
            if t1 is None or t2 is None:
                continue
            gap = round(t1 - t2, 3)
            event = session.event['EventName']
            results.append({
                'event': event,
                'driver1_time': round(t1, 3),
                'driver2_time': round(t2, 3),
                'gap': gap,
                'faster': driver1 if gap <0 else driver2 })
        except:
            continue
    return {
        'driver1': driver1,
        'driver2': driver2,
        'races': results
          }






def get_fastest_lap_history(location, years, session_type='Q'):
  



    results = []
    for year in years:
        try:
            session = get_session(year, location, session_type)
            fastest = session.laps.pick_fastest()

            if fastest is None:
                continue

            lap_time = fastest['LapTime'].total_seconds()
            driver = fastest['Driver']

            results.append({
                'year': year,
                'lap_time': round(lap_time, 3),
                'driver': driver  })

        except:
            continue
    return {
        'location': location,
        'session_type': session_type,
        'history': results
    }
 








def get_driver_circuit_stats(driver, location, years):





    results = []

    for year in years:
        try:
            quali = get_session(year, location, 'Q')
            driver_quali = quali.results[quali.results['Abbreviation'] == driver]

            if driver_quali.empty:
                continue
            quali_pos = driver_quali.iloc[0]['Position']

            race = get_session(year, location, 'R')
            driver_race = race.results[race.results['Abbreviation'] == driver]

            if driver_race.empty:
                continue

            race_pos = driver_race.iloc[0]['Position']
            status = driver_race.iloc[0]['Status']

            driver_laps = get_driver_laps(race, driver)
            driver_laps = driver_laps.copy()
            driver_laps['LapTimeSeconds'] = driver_laps['LapTime'].dt.total_seconds()
            driver_laps = driver_laps.dropna(subset=['LapTimeSeconds'])

            if not driver_laps.empty:
                fastest = round(driver_laps['LapTimeSeconds'].min(), 3)
            else:
                fastest = None
            results.append({
                'year': year,
                'quali_pos': int(quali_pos) if not pd.isna(quali_pos) else None,
                'race_pos': int(race_pos) if not pd.isna(race_pos) else None,
                'fastest_lap': fastest,
                'status': status
            })
        except:
            continue
    return {
        'driver': driver,
        'location': location,
        'history': results
         }













def get_sector_improvement(session, driver):
    

    laps = get_driver_laps(session, driver)
    laps = laps.copy()

    laps['S1'] = laps['Sector1Time'].dt.total_seconds()
    laps['S2'] = laps['Sector2Time'].dt.total_seconds()
    laps['S3'] = laps['Sector3Time'].dt.total_seconds()
    laps = laps.dropna(subset=['S1', 'S2', 'S3', 'Stint', 'TyreLife'])
    laps = laps[laps['TrackStatus'] == '1']
    laps = laps[laps['TyreLife'] > 2]

    results = {}

    for stint in laps['Stint'].unique():
        stint_laps = laps[laps['Stint'] == stint].copy()

        if len(stint_laps) < 3:
            continue
        compound = stint_laps['Compound'].iloc[0]

        results[int(stint)] = {
            'compound': compound,
            'tyre_life': stint_laps['TyreLife'].tolist(),
            's1': stint_laps['S1'].tolist(),
            's2': stint_laps['S2'].tolist(),
            's3': stint_laps['S3'].tolist(),
        
        }

    
    return results








def get_pitstop_performance(session):
  

    laps = session.laps.copy()
    results = []

    drivers = laps['Driver'].unique()

    for driver in drivers:
        driver_laps = laps[laps['Driver'] == driver].copy()
        driver_laps = driver_laps.sort_values('LapNumber')

        for _, row in driver_laps.iterrows():          
            if pd.notna(row['PitInTime']):
                pit_in = row['PitInTime']
                lap_num = int(row['LapNumber'])

                outlap = driver_laps[
                    driver_laps['PitOutTime'].notna()
                      ]
                outlap = outlap[outlap['LapNumber'] == row['LapNumber'] + 1]

                if outlap.empty:
                    continue

                pit_out = outlap.iloc[0]['PitOutTime']
                duration = (pit_out - pit_in).total_seconds()

                if duration < 15 or duration > 60:
                    continue

                results.append({
                    'driver': driver,
                    'lap': lap_num,
                    'duration': round(duration, 3),
                    'compound_new': outlap.iloc[0]['Compound']
                }  )

    results.sort(key=lambda x: x['duration'])
    return results









def get_h2h_career(driver1, driver2, locations, years):
    

    results = {}

    for location in locations:
        d1_wins = 0
        d2_wins = 0
        total = 0

        for year in years:
            try:
                session = get_session(year, location, 'Q')

                d1_row = session.results[session.results['Abbreviation'] == driver1]
                d2_row = session.results[session.results['Abbreviation'] == driver2]

                if d1_row.empty or d2_row.empty:
                    continue

                d1_pos = d1_row.iloc[0]['Position']
                d2_pos = d2_row.iloc[0]['Position']

                if pd.isna(d1_pos) or pd.isna(d2_pos):
                    continue

                if d1_pos < d2_pos:
                    d1_wins += 1
                else:
                    d2_wins += 1

                total += 1

            except:
                continue
        if total > 0:
            results[location.replace(' Grand Prix', '')] = {
                'driver1_wins': d1_wins,
                'driver2_wins': d2_wins,
                'total': total,
                'driver1_pct': round((d1_wins / total) * 100, 1)
            }

    return {
        'driver1': driver1,
        'driver2': driver2,
        'circuits': results
    }







def get_championship_battle(year, drivers, events):



    totals = {driver: 0 for driver in drivers}
    rounds = []

    for event in events:
        try:
            race = get_session(year, event, 'R')
            race_results = race.results
        except:
            continue

        for driver in drivers:
            driver_row = race_results[race_results['Abbreviation'] == driver]
            if not driver_row.empty:
                pts = driver_row.iloc[0]['Points']
                if not pd.isna(pts):
                    totals[driver] += float(pts)

        
        had_sprint = False
        try:
            sprint = get_session(year, event, 'S')
            sprint_results = sprint.results
            had_sprint = True
            for driver in drivers:
                driver_row = sprint_results[sprint_results['Abbreviation'] == driver]
                if not driver_row.empty:
                    pts = driver_row.iloc[0]['Points']
                    if not pd.isna(pts):
                        totals[driver] += float(pts)
        except:
            pass

        
        
        rounds.append({
            'round': len(rounds) + 1,
            'event': event.replace(' Grand Prix', ''),
            'had_sprint': had_sprint,
            'points': {driver: round(totals[driver], 1) for driver in drivers}})

    if not rounds:
        return None

    leader = max(totals, key=totals.get)
    gaps = {driver: round(totals[leader] - totals[driver], 1) for driver in drivers}

    
    
    return {
        'drivers': drivers,
        'rounds': rounds,
        'final_points': {d: round(totals[d], 1) for d in drivers},
        'leader': leader,
        'gaps': gaps
   
       }





def get_overtakes(session):



    
    
    laps = session.laps.copy()
    laps = laps[laps['TrackStatus'] == '1']
    laps = laps.dropna(subset=['Position', 'LapNumber'])

    lap_numbers = sorted(laps['LapNumber'].unique())

    overtakes = []

    for i in range(1, len(lap_numbers)):
        prev_lap = lap_numbers[i - 1]
        curr_lap = lap_numbers[i]

        prev_positions = laps[laps['LapNumber'] == prev_lap][['Driver', 'Position']]
        curr_positions = laps[laps['LapNumber'] == curr_lap][['Driver', 'Position']]

        prev_dict = dict(zip(prev_positions['Driver'], prev_positions['Position']))
        curr_dict = dict(zip(curr_positions['Driver'], curr_positions['Position']))
        pit_drivers = laps[
            (laps['LapNumber'] == curr_lap) &
            (laps['PitInTime'].notna() | laps['PitOutTime'].notna())
        ]['Driver'].tolist()

        drivers = list(curr_dict.keys())

        for a in range(len(drivers)):
            for b in range(a + 1, len(drivers)):
                d1 = drivers[a]
                d2 = drivers[b]

                if d1 not in prev_dict or d2 not in prev_dict:
                    continue
                if d1 in pit_drivers or d2 in pit_drivers:
                    continue

                prev_order = prev_dict[d1] < prev_dict[d2]
                curr_order = curr_dict[d1] < curr_dict[d2]

                if prev_order != curr_order:
                    if curr_order:
                        overtaker, overtaken = d1, d2
                    else:
                        overtaker, overtaken = d2, d1

                    overtakes.append({
                        'lap': int(curr_lap),
                        'overtaker': overtaker,
                        'overtaken': overtaken })

    return overtakes







def get_overtake_summary(overtakes):



    summary = {}

    for ot in overtakes:
        overtaker = ot['overtaker']
        overtaken = ot['overtaken']

        if overtaker not in summary:
            summary[overtaker] = {'overtakes_made': 0, 'times_overtaken': 0}
        if overtaken not in summary:
            summary[overtaken] = {'overtakes_made': 0, 'times_overtaken': 0}

        summary[overtaker]['overtakes_made'] += 1
        summary[overtaken]['times_overtaken'] += 1

    return summary







def get_track_evolution(session, window=5, threshold_pct=115):



    laps = session.laps.copy()
    laps = laps.dropna(subset=['LapTime', 'LapStartTime'])
    laps = laps[laps['IsAccurate'] == True]
    laps = laps[laps['TrackStatus'] == '1']

    laps = laps.copy()
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()

    overall_best = laps['LapTimeSeconds'].min()
    laps = laps[laps['LapTimeSeconds'] <= overall_best * (threshold_pct / 100)]

    laps = laps.sort_values('LapStartTime').reset_index(drop=True)
    laps['SessionBest'] = laps['LapTimeSeconds'].cummin()
    laps['RollingAvg'] = laps['LapTimeSeconds'].rolling(window, min_periods=1).mean()
    return laps[['LapStartTime', 'Driver', 'LapTimeSeconds', 'SessionBest', 'RollingAvg']]

# saat ipol od vchera








def get_drs_effect(session, driver, lap_number=None):



    laps = session.laps.pick_drivers(driver)

    if lap_number is None:
        lap = laps.pick_fastest()
    else:
        lap = laps[laps['LapNumber'] == lap_number].iloc[0]

    telemetry = lap.get_telemetry()
    telemetry = telemetry[['Distance', 'Speed', 'DRS']].dropna()

    drs_open = telemetry['DRS'].isin([10, 12, 14])

    zones = []
    in_zone = False
    zone_start_idx = None

    for i, is_open in enumerate(drs_open):
        if is_open and not in_zone:
            in_zone = True
            zone_start_idx = i
        elif not is_open and in_zone:
            in_zone = False
            zone_telemetry = telemetry.iloc[zone_start_idx:i]

            if len(zone_telemetry) < 2:
                continue

            entry_speed = zone_telemetry['Speed'].iloc[0]
            peak_speed = zone_telemetry['Speed'].max()
            exit_speed = zone_telemetry['Speed'].iloc[-1]

            zones.append({
                'distance_start': round(zone_telemetry['Distance'].iloc[0], 1),
                'distance_end': round(zone_telemetry['Distance'].iloc[-1], 1),
                'entry_speed': round(entry_speed, 1),
                'peak_speed': round(peak_speed, 1),
                'exit_speed': round(exit_speed, 1),
                'speed_gain': round(peak_speed - entry_speed, 1)})

    if in_zone:
        zone_telemetry = telemetry.iloc[zone_start_idx:]
        if len(zone_telemetry) >= 2:
            entry_speed = zone_telemetry['Speed'].iloc[0]
            peak_speed = zone_telemetry['Speed'].max()
            exit_speed = zone_telemetry['Speed'].iloc[-1]
            zones.append({
                'distance_start': round(zone_telemetry['Distance'].iloc[0], 1),
                'distance_end': round(zone_telemetry['Distance'].iloc[-1], 1),
                'entry_speed': round(entry_speed, 1),
                'peak_speed': round(peak_speed, 1),
                'exit_speed': round(exit_speed, 1),
                'speed_gain': round(peak_speed - entry_speed, 1)})

    return {
        'driver': driver,
        'lap_number': int(lap['LapNumber']),
        'zones': zones,
        'telemetry': telemetry
    }