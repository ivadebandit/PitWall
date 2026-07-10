import pandas as pd
import numpy as np
from fetch import get_session, get_driver_laps

def get_clean_laps(session, driver):
    """
    Returns only clean, accurate laps for a driver.
    Filters out safety car laps, deleted laps and inaccurate laps.

    session = session object from get_session()
    driver = three letter driver code e.g. 'VER'
    """
    # Get all laps for this driver
    laps = get_driver_laps(session, driver)

    # Filter 1 - only keep laps FastF1 considers accurate
    laps = laps[laps['IsAccurate'] == True]

    # Filter 2 - remove deleted laps (track limits etc)
    laps = laps[laps['Deleted'] == False]

    # Filter 3 - only keep green flag laps
    # TrackStatus '1' means green flag
    # anything else means SC, VSC, red flag etc
    laps = laps[laps['TrackStatus'] == '1']

    # Filter 4 - remove laps with no lap time recorded
    laps = laps.dropna(subset=['LapTime'])

    return laps

def get_race_pace(session, driver):
    """
    Calculates average lap time per stint for a driver
    Returns a DataFrame with stint number, compound and avg lap time

    session = session object from get_session()
    driver  = three letter driver code e.g. 'VER'
    """
    laps = get_clean_laps(session, driver)

    laps = laps.copy()
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()

    pace = laps.groupby('Stint').agg(
        AvgLapTime=('LapTimeSeconds', 'mean'),
        Compound=('Compound', 'first'),
        LapCount=('LapNumber', 'count')
    ).reset_index()

    return pace

def get_head_to_head(session, driver1, driver2):
    """
    Compares lap by lap times between two drivers.
    Returns both drivers' clean laps merged together.

    session = session object from get_session()
    driver1 = three letter code for first driver e.g. 'VER'
    driver2 = three letter code for second driver e.g. 'ALO'
    """
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
    """
    Calculates how consistent a driver's lap times were.
    Lower score = more consistent.
    Uses standard deviation of clean lap times
    
    session = session object from get_session()
    driver  = three letter driver code
    """

    laps = get_clean_laps(session, driver)

    laps = laps.copy()
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()

    score = laps['LapTimeSeconds'].std()

    return round(score, 3)

def get_h2h_summary(session, driver1, driver2):
    """
    Returns an overall race pace summary between two drivers
    Shows average lap time, difference and who was faster

    session = session object from get_session()
    driver1 = three letter code
    driver2 = three letter code
    """
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
    """
    Gets the best qualifying lap for a driver
    Returns the fastest lap with full sector times

    session = session object from get_session()
    driver = three letter driver code
    """

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
    """
    Returns lap by kao position data for a driver.
    Shows how they moved through the field during the race

    session = session object from get_session()
    driver  = three letter driver code
    """

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
    """
    Gets telemetry data for a specific lap object.
    Returns telemetry with Distance, Speed, Throttle, Brake, nGear.

    lap = a single lap row  from FastF1 laps DataFrame
    """
    telemetry = lap.get_telemetry()

    telemetry = telemetry[['Distance', 'Speed', 'Throttle', 'Brake', 'nGear']].copy()

    telemetry = telemetry.dropna()

    return telemetry

def interpolate_telemetry(telemetry, distance_grid):
    """
    Interpolates telemetry data onto a common distance grid.
    This lets us compare two laps at the exact track positions.

    telemetry     = telemetry DataFrame from get_telemetry_for_lap()
    distance_grid = array of evenly spaced distance points to interpolate into
    """

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
    """
    Finds the nearest corner number for a given distance on track.

    circuit_info = session.get_circuit_info()
    distance     = distance along the track in meters
    """

    corners = circuit_info.corners

    corners = corners.copy()
    corners['diff'] = abs(corners['Distance'] - distance)

    nearest = corners.loc[corners['diff'].idxmin()]

    turn_number = int(nearest['Number'])
    corner_distance = round(nearest['Distance'], 1)

    return turn_number, corner_distance




def detect_mistakes(session, driver, lap_number=None):
    """
    Detects mistakes in a driver's lap by comparing it to their best lap.
    Returns a list of mistakes with location and time lost.

    session    = session object from get_session()
    driver     = three letter driver code e.g. 'VER'
    lap_number = specific lap to analyze, if None uses second best lap
    """

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
    """
    Builds the theoretical perfect lap from a driver's best sectors.
    Returns best S1, S2, S3 and the combined perfect lap time.

    session = session object 
    driver  = three letter driver code
    """

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


