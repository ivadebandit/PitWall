import pandas as pd
import numpy as np
from fetch import get_session, get_driver_laps



def get_clean_laps(session,driver):
    laps= get_driver_laps(session, driver)
    laps = laps[laps['IsAccurate'] == True]
    laps = laps[laps['Deleted'] == False]
    laps= laps[laps['TrackStatus'] == '1']

    laps = laps.dropna(subset=['LapTime'])
    laps = laps.copy()
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()
    best_time = laps['LapTimeSeconds'].min()
    laps = laps[laps['LapTimeSeconds'] <= best_time * 1.15]
    return laps.drop(columns=['LapTimeSeconds'])





def get_race_pace(session, driver):
    laps = get_clean_laps(session, driver)
    laps = laps.copy()
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()
    pace= laps.groupby('Stint').agg(
        AvgLapTime=('LapTimeSeconds', 'mean'),
        Compound = ('Compound', 'first'),
        Lapcount=('LapNumber', 'count')
    ).reset_index()
    return pace





def get_head_to_head(session, driver1, driver2):
    
    
    
    laps1 = get_clean_laps(session,driver1)
    laps2 = get_clean_laps(session,driver2)
    laps1 = laps1.copy()
    laps2 = laps2.copy()
    laps1['LapTimeSeconds'] =laps1['LapTime'].dt.total_seconds()
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

    return round(score,3)






def get_h2h_summary(session,driver1,driver2):
    laps1 = get_clean_laps(session,driver1)
    laps2 = get_clean_laps(session,driver2)
    laps1 = laps1.copy()
    laps2 = laps2.copy()
    laps1['LapTimeSeconds'] = laps1['LapTime'].dt.total_seconds()
    laps2['LapTimeSeconds'] = laps2['LapTime'].dt.total_seconds()
    avg1 = laps1['LapTimeSeconds'].mean()
    avg2 = laps2['LapTimeSeconds'].mean()
    diff = abs(avg1-avg2)
    if avg1 < avg2:
        faster = driver1
    else:
        faster = driver2
    summary = {
        'driver1': round(avg1, 3),
        'driver2': round(avg2, 3),
        'gap': round(diff, 3),
        'faster_driver': faster}
    return summary

    


def get_position_change(session, driver):
    laps= get_driver_laps(session,driver)
    laps = laps.copy()
    position_data = laps[['LapNumber', 'Position']].dropna()
    driver_info = session.get_driver(driver)
    grid_position= driver_info['GridPosition']
    start_row = pd.DataFrame({
        'LapNumber': [0],
        'Position': [grid_position]})
    position_data= pd.concat([start_row, position_data]).reset_index(drop=True)
    return position_data





def get_quali_laps(session, driver):
    laps = get_driver_laps(session,driver)
    laps = laps.copy()
    laps['S1']=laps['Sector1Time'].dt.total_seconds()
    laps['S2']=laps['Sector2Time'].dt.total_seconds()
    laps['S3']=laps['Sector3Time'].dt.total_seconds()
    laps['LapTimeSeconds']=laps['LapTime'].dt.total_seconds()
    laps = laps.dropna(subset=['S1', 'S2', 'S3'])
    best_lap = laps.loc[laps['LapTimeSeconds'].idxmin()]
    return best_lap



import numpy as np
from scipy import interpolate



def get_telemetry_for_lap(lap):
    telemetry = lap.get_telemetry()
    telemetry = telemetry[['Distance', 'Speed', 'Throttle', 'Brake', 'nGear']].copy()
    telemetry = telemetry.dropna()
    return telemetry



# do pet i dvaese

def interpolate_telemetry(telemetry, distance_grid):
    speed_interp = interpolate.interp1d(
        telemetry['Distance'],
        telemetry['Speed'],
        kind='linear',
        fill_value='extrapolate')
    throttle_interp= interpolate.interp1d(
        telemetry['Distance'],
        telemetry['Throttle'],
        kind='linear',
        fill_value="extrapolate")
    brake_interp = interpolate.interp1d(
        telemetry['Distance'],
        telemetry['Speed'],
        kind='linear',
        fill_value='extrapolate')
    gear_interp= interpolate.interp1d(
        telemetry['Distance'],
        telemetry['nGear'],
        kind='linear',
        fill_value='extrapolate')
    result = pd.DataFrame({
        'Distance': distance_grid,
        'Speed': speed_interp(distance_grid),
        'Throttle': throttle_interp(distance_grid),
        'Brake': brake_interp(distance_grid),
        'nGear': gear_interp(distance_grid)})
    return result


    