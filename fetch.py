import fastf1
import pandas as pd

def get_session(year, location, session_type):
    """
    Fetches a session from FastF1

    year         = the session year e.g. 2023
    location     = the race name e.g. 'Monaco'
    session_type = 'R' for race, 'Q' for qualifying
    """
    session = fastf1.get_session(year, location, session_type)

    session.load(laps=True, telemetry=True, weather=True)

    return session

def get_driver_laps(session, driver):
    """
    Gets all laps for a specific driver from a session.

    session = the session object we got from get_session()
    driver  = three letter driver code e.g. 'VER', 'ALO'
    """
    laps =  session.laps.pick_drivers(driver)

    return laps






