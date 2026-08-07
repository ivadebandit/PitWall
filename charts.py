import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.collections as mc
import numpy as np
from analyze import get_clean_laps, get_race_pace, get_h2h




COLORS = {
    'background': '#0a0a0a',
    'paper': '#111111',
    'text': '#ffffff',
    'text_secondary': '#888888',
    'grid': '#1a1a1a',
    'border': '#2a2a2a',
    'red': '#e8002d',
    'green': '#2ecc71',
    'yellow': '#ffd700',
    'purple': '#9b59b6',
    'cyan': '#00d4ff',
    'soft': '#ff3333',
    'medium': '#ffd700',
    'hard': '#ffffff',
    'inter': '#00d632',
    'wet': "#0752C1",
}


TEAM_COLORS ={
    'Mercedes': '#00d2be',
    'Ferrari': '#e8002d',
    'Red Bull Racing': '#3671c6',
    'Red Bull': "#3671c6",
    'McLaren': '#ff8000',
    'Aston Martin': '#358c75',
    'Racing Point': '#f596c8',
    'Force India': '#ff80c7',
    'Alpine': '#ff87bc',
    'Renault': '#fff500',
    'Williams': '#64c4ff',
    'Racing Bulls': '#6692ff',
    'AlphaTauri': '#5c37a3',
    'Toro Rosso': '#1e3d61',
    'Haas': '#b6babd',
    'Haas F1 Team': '#b6babd',
    'Kick Sauber': '#52e252',
    'Alfa Romeo': '#c92d4b',
    'Sauber': '#c92d4b',
}


DEFAULT_COLORS = [
    '#E8002D', '#00D632', '#FFD700', '#00D4FF', '#9B59B6',
    '#FF6B6B', '#51CF66', '#FCC419', '#339AF0', '#CC5DE8'
]



def get_driver_color(session, driver):
    try:
        driver_info = session.get_driver(driver)
        color = driver_info['TeamColor']
        return f"#{color}"
    except:
        return DEFAULT_COLORS[0]






def apply_f1_theme(fig):

    fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['paper'],
        font=dict(
            color=COLORS['text'],
            family='Arial Black, Arial, sans-serif',
            size=13),

        xaxis=dict(
            gridcolor=COLORS['grid'],
            zerolinecolor=COLORS['grid'],
            linecolor=COLORS['border'],
            tickcolor=COLORS['text_secondary'],
            tickfont=dict(size=11)),

        yaxis=dict(
            gridcolor=COLORS['grid'],
            zerolinecolor=COLORS['grid'],
            linecolor=COLORS['border'],
            tickcolor=COLORS['text_secondary'],
            tickfont=dict(size=11)
        ),
        legend=dict(
            bgcolor=COLORS['paper'],
            bordercolor=COLORS['border'],
            borderwidth=1,
            font=dict(size=12)),
        title=dict(
            font=dict(
                size=18,
                family='Arial Black, Arial, sans-serif',
                color=COLORS['text'])))
    return fig









