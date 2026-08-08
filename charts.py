import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.collections as mc
import numpy as np
from analyze import get_clean_laps, get_race_pace, get_head_to_head, get_consistency_score, get_position_change




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





def chart_race_pace(session, driver):
    laps = get_clean_laps(session, driver)
    laps = laps.copy()
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()
    laps = laps.dropna(subset=['LapTimeSeconds'])
    color = get_driver_color(session, driver)
    compound_colors = {
        'SOFT': COLORS['soft'],
        'MEDIUM': COLORS['medium'],
        'HARD': COLORS['hard'],
        'INTERMEDIATE': COLORS['inter'],
        'WET': COLORS['wet']}
    fig = go.Figure()
    for stint in laps['Stint'].unique():
        stint_laps = laps[laps['Stint'] == stint]
        if stint_laps.empty:
            continue
        compound = stint_laps['Compound'].iloc[0]
        stint_color = compound_colors.get(compound, color)
        flying_laps = stint_laps[
            stint_laps['PitInTime'].isna() &
            stint_laps['PitOutTime'].isna()]
        pit_laps = stint_laps[
            stint_laps['PitInTime'].notna() |
            stint_laps['PitOutTime'].notna()]
        if not flying_laps.empty:
            fig.add_trace(go.Scatter(
                x=flying_laps['LapNumber'],
                y=flying_laps['LapTimeSeconds'],
                mode='lines+markers',
                name=f"Stint {int(stint)} - {compound}",
                line=dict(color=stint_color, width=2),
                marker=dict(size=4),
                hovertemplate='Lap %{x}<br>Time: %{y:.3f}s<extra></extra>'))
        if not pit_laps.empty:
            fig.add_trace(go.Scatter(
                x=pit_laps['LapNumber'],
                y=pit_laps['LapTimeSeconds'],
                mode='markers',
                name=f"Pit lap (Stint {int(stint)})",
                marker=dict(size=8, color='#888888', symbol='x'),
                hovertemplate='Lap %{x}<br>Pit lap: %{y:.3f}s<extra></extra>'))
    fig.update_layout(
        title=f"{driver} Race Pace",
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (seconds)",)
    fig = apply_f1_theme(fig)
    return fig






def chart_consistency(session, drivers):
    fig = go.Figure()
    used_colors = []
    for driver in drivers:
        score = get_consistency_score(session,driver)
        color = get_driver_color(session,driver)
        if color.lower() in [c.lower() for c in used_colors]:
            opacity = 0.5
        else:
            opacity = 1.0   
        used_colors.append(color)
        fig.add_trace(go.Bar(   
            x=[driver],
            y=[score],
            name=driver,
            marker=dict(
                color=color,
                opacity=opacity,
                line=dict(color='white', width=1.5)),
                hovertemplate='%{x}<br>Consistency: %{y:.3f}s<extra></extra>'))
    fig.update_layout(
        title="Driver Consistency Comparison",
        xaxis_title="Driver",
        yaxis_title="Std Devtiatiom (lower= more consistent)",)
    fig=apply_f1_theme(fig)
    return fig






def chart_head_to_head(session, driver1, driver2):
    combined = get_head_to_head(session, driver1, driver2)
    color1 = get_driver_color(session, driver1)
    color2 = get_driver_color(session, driver2)
    same_team = color1.lower() == color2.lower()
    fig = go.Figure()
    d1_laps = combined[combined['Driver']==driver1]
    fig.add_trace(go.Scatter(
        x=d1_laps['LapNumber'],
        y=d1_laps['LapTimeSeconds'],
        mode='lines+markers',
        name=driver1,
        line=dict(color=color1, width=2),
        marker=dict(size=4),
        hovertemplate='Lap %{x}<br>Time: %{y:.3f}s<extra></extra>'))
    d2_laps = combined[combined['Driver']==driver2]
    fig.add_trace(go.Scatter(
        x=d2_laps['LapNumber'],
        y=d2_laps['LapTimeSeconds'],
        mode='lines+markers',
        name=driver2,
        line=dict(
            color=color2,
            width=2,
            dash='dash' if same_team else 'solid'),
        marker=dict(size=4),
        hovertemplate='Lap %{x}<br>Time: %{y:.3f}s<extra></extra>'))
    fig.update_layout(
        title=f"{driver1} vs {driver2} Race Pace",
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (seconds)",)
    fig = apply_f1_theme(fig)
    return fig





def chart_position_change(session, drivers):
    fig = go.Figure()
    used_colors = []
    for driver in drivers:
        position_data = get_position_change(session, driver)
        color = get_driver_color(session, driver)
        if color.lower() in [c.lower() for c in used_colors]:
            dash_style = 'dash'       
        else:
            dash_style = 'solid'
        used_colors.append(color)
        fig.add_trace(go.Scatter(
            x=position_data['LapNumber'],
            y=position_data['Position'],
            mode='lines',
            name=driver,
            line=dict(color=color, width=2, dash=dash_style),
            hovertemplate='Lap %{x}<br>Position: P%{y}<extra></extra>'))
    fig.update_layout(
        title="Position Changes During Race",
        xaxis_title="Lap Number",
        yaxis_title="Position",
        yaxis=dict(autorange='reversed'))
    fig = apply_f1_theme(fig)
    return fig