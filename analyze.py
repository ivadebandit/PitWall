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
    # Get clean laps using the already existing function
    laps = get_clean_laps(session, driver)

    # Convert LapTime from a time value to plain seconds
    # e.g. 0 days 00:01:14:123000 becomes 14.123
    # This makes it a lot easier to work with the data
    laps = laps.copy()
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()

    # Froup laps by stint and calculate avg lap time per stint
    # Also grab the compound used in each stint
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
    # Get clean laps for both drivers separately
    laps1 = get_clean_laps(session, driver1)
    laps2 = get_clean_laps(session, driver2)

    # Convert lap times to seconds for both
    laps1 = laps1.copy()
    laps2 = laps2.copy()
    laps1['LapTimeSeconds'] = laps1['LapTime'].dt.total_seconds()
    laps2['LapTimeSeconds'] = laps2['LapTime'].dt.total_seconds()

    # Add a column to each so we know which driver is which
    # after we combine all of the laps
    laps1['Driver'] = driver1
    laps2['Driver'] = driver2

    # Stack both DataFrames on top of each other into one combined table
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

    # Get clean laps
    laps = get_clean_laps(session, driver)

    # Convert to seconds
    laps = laps.copy()
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()

    # Standard deviation measures how spread out lap times are
    # If all laps are similar the std is low = very consistent
    # If lap times jump around a lot the std is high = inconsistent
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
    # Get clean laps for both drivers
    laps1 = get_clean_laps(session, driver1)
    laps2 = get_clean_laps(session, driver2)

    # Convert to seconds for both
    laps1 = laps1.copy()
    laps2 = laps2.copy()
    laps1['LapTimeSeconds'] = laps1['LapTime'].dt.total_seconds()
    laps2['LapTimeSeconds'] = laps2['LapTime'].dt.total_seconds()

    # Calculate average lap time for both drivers
    avg1 = laps1['LapTimeSeconds'].mean()
    avg2 = laps2['LapTimeSeconds'].mean()

    # Calculate the gap between them
    diff = abs(avg1 - avg2)

    # Figure out who was faster
    faster = driver1 if avg1 < avg2 else driver2

    # Summary 
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

    # Get all laps for this driver
    laps = get_driver_laps(session, driver)

    # Convert sector times to seconds
    laps = laps.copy()
    laps['S1'] = laps['Sector1Time'].dt.total_seconds()
    laps['S2'] = laps['Sector2Time'].dt.total_seconds()
    laps['S3'] = laps['Sector3Time'].dt.total_seconds()
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()

    # Drop rows with missing sector times
    laps = laps.dropna(subset=['S1', 'S2', 'S3'])

    # Get the single fastest lap
    best_lap = laps.loc[laps['LapTimeSeconds'].idxmin()]

    return best_lap    

def get_position_change(session, driver):
    """
    Returns lap by kao position data for a driver.
    Shows how they moved through the field during the race

    session = session object from get_session()
    driver  = three letter driver code
    """

    # Get all laps
    laps = get_driver_laps(session, driver)
    laps = laps.copy()

    # Get position data
    position_data = laps[['LapNumber', 'Position']].dropna()

    # Get starting grid position
    driver_info = session.get_driver(driver)
    grid_position = driver_info['GridPosition']

    # Create a lap 0 aka starting position
    start_row = pd.DataFrame({
        'LapNumber': [0],
        'Position': [grid_position]
    })

    # Add grid position as lap 0 at the top of the data
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
    # Get full telemetry for this lap
    telemetry = lap.get_telemetry()

    # Keep only the columns we need
    telemetry = telemetry[['Distance', 'Speed', 'Throttle', 'Brake', 'nGear']].copy()

    # Drop any rows with missing values
    telemetry = telemetry.dropna()

    return telemetry

def interpolate_telemetry(telemetry, distance_grid):
    """
    Interpolates telemetry data onto a common distance grid.
    This lets us compare two laps at the exact track positions.

    telemetry     = telemetry DataFrame from get_telemetry_for_lap()
    distance_grid = array of evenly spaced distance points to interpolate into
    """

    # Create interpolation functions for each channel
    # 'linear' means draw straight lines between data points
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

    
    # Apply each interpolation function to the distance grid
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

    # Calculate absolute difference between mistake distance
    # and every corner's distance
    corners = corners.copy()
    corners['diff'] = abs(corners['Distance'] - distance)

    # Get the corner with the smallest difference
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

    # Get all laps for this driver
    laps = session.laps.pick_drivers(driver)

    # Get the best lap as our reference
    best_lap = laps.pick_fastest()

    # If no lap number specified, use the second fastest lap
    if lap_number is None:
        # Sort laps by time and take the second one
        sorted_laps = laps.sort_values('LapTime').dropna(subset=['LapTime'])
        if len(sorted_laps) < 2:
            return []
        comparison_lap = sorted_laps.iloc[1]
    else:
        # Use the specific lap number requested
        comparison_lap = laps[laps['LapNumber'] == lap_number].iloc[0]

    # Get telemetry for both laps
    best_telemetry = get_telemetry_for_lap(best_lap)
    comp_telemetry = get_telemetry_for_lap(comparison_lap)

    # Create a common distance grid based on the shorter lap
    max_distance = min(
        best_telemetry['Distance'].max(),
        comp_telemetry['Distance'].max()
    )
    distance_grid = np.arange(0, max_distance, 10)

    # Interpolate both laps onto the same grid
    best_interp = interpolate_telemetry(best_telemetry, distance_grid)
    comp_interp = interpolate_telemetry(comp_telemetry, distance_grid)

    # Calculate speed difference at every point
    # Negative means comparison lap was slower than best lap
    speed_diff = comp_interp['Speed'] - best_interp['Speed']

    # Find where the comparison lap was significantly slower
    # Threshold of 5 km/h difference flags a potential mistake
    mistake_threshold = -5.0
    mistake_mask = speed_diff < mistake_threshold

    # Find groups of consecutive mistake points
    mistakes = []
    in_mistake = False
    mistake_start = None
    mistake_start_idx = None

    circuit_info = session.get_circuit_info()
    for i, (is_mistake, distance) in enumerate(zip(mistake_mask, distance_grid)):
        if is_mistake and not in_mistake:
            # Start of a new mistake zone
            in_mistake = True
            mistake_start = distance
            mistake_start_idx = i

        elif not is_mistake and in_mistake:
            # End of mistake zone
            in_mistake = False
            mistake_end = distance

            # Find the worst point in this mistake zone
            zone_diff = speed_diff.iloc[mistake_start_idx:i]
            worst_speed_loss = zone_diff.min()
            worst_distance = distance_grid[mistake_start_idx + zone_diff.argmin()]

            # Estimate time lost using the speed difference
            # time = distance / speed, so losing speed costs time
            zone_length = mistake_end - mistake_start
            avg_speed_loss = abs(zone_diff.mean())

            # Convert km/h to m/s for time calculation
            avg_best_speed = best_interp['Speed'].iloc[mistake_start_idx:i].mean()
            avg_comp_speed = comp_interp['Speed'].iloc[mistake_start_idx:i].mean()

            if avg_comp_speed > 0 and avg_best_speed > 0:
                time_best = zone_length / (avg_best_speed / 3.6)
                time_comp = zone_length / (avg_comp_speed / 3.6)
                time_lost = round(time_comp - time_best, 3)
            else:
                time_lost = 0

            # Only record mistakes where meaningful time was lost
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

    # Sort by time lost so biggest mistakes come first
    mistakes.sort(key=lambda x: x['time_lost'], reverse=True)

    return mistakes

    
    


