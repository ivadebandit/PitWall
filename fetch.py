import fastf1
import pandas as pd

def get_session(year, location, session_type, light=False):
    session = fastf1.get_session(year, location, session_type)

    if light:
        session.load(laps=True, telemetry=False, weather=False)
    else:
        session.load(laps=True, telemetry=True, weather=True)

    return session
def get_driver_laps(session, driver):
    laps =  session.laps.pick_drivers(driver)
    return laps

  
  
 
 


