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