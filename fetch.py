import fastf1
import pandas as pd

# This tells FastF1 where to save cached data
# It creates a folder called 'cache' inside my Pitwall folder
# fastf1.Cache.enable_cache('cache')

def get_session(year, location, session_type):
    """
    Fetches a session from FastF1

    year         = the session year e.g. 2023
    location     = the race name e.g. 'Monaco'
    session_type = 'R' for race, 'Q' for qualifying
    """
    # This loads the session, like opening a specific race weekend
    session = fastf1.get_session(year, location, session_type)

    # This actually downloads all the data for that session
    # laps=True means get lap time data
    # telemetry=True means get the detailed car data (speed, throttle, brake etc)
    # weather=True means get track temperature, air temp, humidity
    session.load(laps=True, telemetry=True, weather=True)

    return session

def get_driver_laps(session, driver):
    """
    Gets all laps for a specific driver from a session.

    session = the session object we got from get_session()
    driver  = three letter driver code e.g. 'VER', 'ALO'
    """
    # session.laps gives us all laps from all drivers
    # .pick_drivers() filters it down just to the driver we want
    laps =  session.laps.pick_drivers(driver)

    return laps






