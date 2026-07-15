import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.collections as mc
import numpy as np
from analyze import get_clean_laps, get_race_pace, get_head_to_head, get_h2h_summary, get_consistency_score
from analyze import get_quali_laps, get_position_change, get_driver_laps, detect_mistakes


COLORS = {
    'background': '#0a0a0a',
    'paper': '#111111',
    'text': '#FFFFFF',
    'text_secondary': '#888888',
    'grid': '#1a1a1a',
    'border': '#2a2a2a',
    'red': '#E8002D',
    'green': '#2ECC71',
    'yellow': '#FFD700',
    'purple': '#9B59B6',
    'cyan': '#00D4FF',
    'soft': '#FF3333',
    'medium':'#FFD700',
    'hard': '#FFFFFF',
    'inter': '#00D632',
    'wet': '#00D4FF',
}


TEAM_COLORS = {
    'Mercedes': '#00D2BE',
    'Ferrari': '#E8002D',
    'Red Bull Racing': '#3671C6',
    'Red Bull': '#3671C6',
    'McLaren': '#FF8000',
    'Aston Martin': '#358C75',
    'Racing Point': '#F596C8',
    'Force India': '#FF80C7',
    'Alpine': '#FF87BC',
    'Renault': '#FFF500',
    'Williams': '#64C4FF',
    'Racing Bulls': '#6692FF',
    'AlphaTauri': '#5C37A3',
    'Toro Rosso': '#1E3D61',
    'Haas F1 Team': '#B6BABD',
    'Haas': '#B6BABD',
    'Kick Sauber': '#52E252',
    'Alfa Romeo': '#C92D4B',
    'Sauber': '#C92D4B',
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
            size=13
        ),
        xaxis=dict(
            gridcolor=COLORS['grid'],
            zerolinecolor=COLORS['grid'],
            linecolor=COLORS['border'],
            tickcolor=COLORS['text_secondary'],
            tickfont=dict(size=11)
        ),
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
            font=dict(size=12)
        ),
        title=dict(
            font=dict(
                size=18,
                family='Arial Black, Arial, sans-serif',
                color=COLORS['text']
            )
        )
    )

    return fig

def chart_race_pace(session, driver):
    laps = get_driver_laps(session, driver)
    laps = laps.copy()
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()

    laps = laps.dropna(subset=['LapTimeSeconds'])

    color = get_driver_color(session, driver)

    compound_colors = {
        'SOFT': COLORS['soft'],
        'MEDIUM': COLORS['medium'],
        'HARD': COLORS['hard'],
        'INTERMEDIATE': COLORS['inter'],
        'WET': COLORS['wet']
    }

    fig = go.Figure()

    for stint in laps['Stint'].unique():
        stint_laps = laps[laps['Stint'] == stint]

        if stint_laps.empty:
            continue
        
        compound = stint_laps['Compound'].iloc[0]
        stint_color = compound_colors.get(compound, color)

        flying_laps = stint_laps[
            stint_laps['PitInTime'].isna() &
            stint_laps['PitOutTime'].isna()
        ]
        pit_laps = stint_laps[
            stint_laps['PitInTime'].notna() | 
            stint_laps['PitOutTime'].notna()
        ]

        if not flying_laps.empty:
            fig.add_trace(go.Scatter(
                x=flying_laps['LapNumber'],
                y=flying_laps['LapTimeSeconds'],
                mode='lines+markers',
                name=f"Stint {int(stint)} - {compound}",
                line=dict(color=stint_color, width=2),
                marker=dict(size=4),
                hovertemplate='Lap %{x}<br>Time: %{y:.3f}s<extra></extra>'
            ))

        if not pit_laps.empty:
            fig.add_trace(go.Scatter(
                x=pit_laps['LapNumber'],
                y=pit_laps['LapTimeSeconds'],
                mode='markers',
                name=f"Pit lap (Stint {int(stint)})",
                marker=dict(size=8, color='#888888', symbol='x'),
                hovertemplate='Lap %{x}<br>Pit lap: %{y:.3f}s<extra></extra>'
            ))

    fig.update_layout(
        title=f"{driver} Race Pace",
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (seconds)",
    )

    fig = apply_f1_theme(fig)

    return fig
    

            

        



def chart_head_to_head(session, driver1, driver2):
  
    combined = get_head_to_head(session, driver1, driver2)

    color1 = get_driver_color(session, driver1)
    color2 = get_driver_color(session, driver2)

    same_team = color1.lower() == color2.lower()

    fig = go.Figure()

    d1_laps = combined[combined['Driver'] == driver1]
    fig.add_trace(go.Scatter(
        x=d1_laps['LapNumber'],
        y=d1_laps['LapTimeSeconds'],
        mode='lines+markers',
        name=driver1,
        line=dict(color=color1, width=2),
        marker=dict(size=4),
        hovertemplate='Lap %{x}<br>Time: %{y:.3f}s<extra></extra>'
    ))

    d2_laps = combined[combined['Driver'] == driver2]
    fig.add_trace(go.Scatter(
        x=d2_laps['LapNumber'],
        y=d2_laps['LapTimeSeconds'],
        mode='lines+markers',
        name=driver2,
        line=dict(
            color=color2,
            width=2,
            dash='dash' if same_team else 'solid'
        ),
        marker=dict(size=4),
        hovertemplate='Lap %{x}<br>Time: %{y:.3f}s<extra></extra>'
    ))

    fig.update_layout(
        title=f"{driver1} vs {driver2} Race Pace",
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (seconds)",
    )

    fig = apply_f1_theme(fig)

    return fig

def chart_consistency(session, drivers):
    
    fig = go.Figure()

    used_colors = []

    for driver in drivers:
        score = get_consistency_score(session, driver)
        color = get_driver_color(session, driver)

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
                line=dict(color='white', width=1.5)
            ),
            hovertemplate='%{x}<br>Consistency: %{y:.3f}s<extra></extra>'
        ))

    fig.update_layout(
        title="Driver Consistency Comparison",
        xaxis_title="Driver",
        yaxis_title="Std Deviation (lower = more consistent)",
    )

    
    
    fig = apply_f1_theme(fig)

    return fig





def chart_quali_comparison(session, driver1, driver2):  
  
    lap1 = get_quali_laps(session, driver1)
    lap2 = get_quali_laps(session, driver2)

    color1 = get_driver_color(session, driver1)
    color2 = get_driver_color(session, driver2)

    sectors = ['Sector 1', 'Sector 2', 'Sector 3']

    times1 = [lap1['S1'], lap1['S2'], lap1['S3']]
    times2 = [lap2['S1'], lap2['S2'], lap2['S3']]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=sectors,
        y=times1,
        name=driver1,
        marker=dict(color=color1),
        hovertemplate='%{x}<br>Time: %{y:.3f}s<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=sectors,
        y=times2,
        name=driver2,
        marker=dict(color=color2),
        hovertemplate='%{x}<br>Time: %{y:.3f}s<extra></extra>'
    ))

    fig.update_layout(
        title=f"{driver1} vs {driver2} Qualifying Sectors",
        xaxis_title="Sector",
        yaxis_title="Time (seconds)",
        barmode='group'
    )

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
            hovertemplate='Lap %{x}<br>Position: P%{y}<extra></extra>'
        ))

    
    fig.update_layout(
        title="Position Changes During Race",
        xaxis_title="Lap Number",
        yaxis_title="Position",
        yaxis=dict(autorange='reversed')
    )

    fig = apply_f1_theme(fig)

    
    
    return fig




def chart_track_mistakes(session, driver):
    """
    Draws the circuit map colored by speed with mistake zones highlighted.
    Saves the chart as a PNG file.

    session = session object from get_session()
    driver  = three letter driver code e.g. 'VER'
    """

    laps = session.laps.pick_drivers(driver)
    best_lap = laps.pick_fastest()

    telemetry = best_lap.get_telemetry().add_distance()

    mistakes = detect_mistakes(session, driver)

    circuit_info = session.get_circuit_info()

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')

    x = telemetry['X'].values
    y = telemetry['Y'].values
    speed = telemetry['Speed'].values
    distance = telemetry['Distance'].values

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    norm = plt.Normalize(speed.min(), speed.max())
    lc = mc.LineCollection(
        segments,
        cmap='RdYlGn', # red = slow, yellow = medium, green = fast
        norm=norm,
        linewidth=3,
        zorder=2
    )
    lc.set_array(speed[:-1])
    ax.add_collection(lc)

    cbar = plt.colorbar(lc, ax=ax)
    cbar.set_label('Speed (km/h)', color='white')
    cbar.ax.yaxis.set_tick_params(color='white')
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')

    for mistake in mistakes:
            mask = (
                (distance >= mistake['distance_start']) &
                (distance <= mistake['distance_end'])
            )
            mistake_x = x[mask]
            mistake_y = y[mask]

            if len(mistake_x) > 0:
                ax.plot(
                    mistake_x, mistake_y,
                    color='#E8002D',
                    linewidth=6,
                    zorder=3,
                    alpha=0.8
                )

                worst_mask = np.abs(distance - mistake['worst_point']) < 20
                if worst_mask.any():
                    label_x = x[worst_mask][0]
                    label_y = y[worst_mask][0]
                    ax.annotate(
                        f"T{mistake['turn_number']}\n-{mistake['time_lost']}s",
                        xy=(label_x, label_y),
                        color='white',
                        fontsize=8,
                        fontweight='bold',
                        bbox=dict(
                            boxstyle='square,pad=0.3',
                            facecolor=COLORS['red'],
                            alpha=1.0
                       
                        ),
                        zorder=5
                  
                    )
            
            
            
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_title(
                f"{driver} - Mistake Analysis",
                color='white',
                fontsize=14,
                pad=20
            )

           
           
            plt.tight_layout()
            plt.savefig(
                f"{driver}_mistakes.png",
                dpi=150,
                bbox_inches='tight',
                facecolor='#1a1a2e'
            )
            plt.show()

           
           
            return f"{driver}_mistakes.png"
    



def  chart_perfect_lap(session, driver):


    from analyze import get_perfect_lap, get_quali_laps

    result = get_perfect_lap(session, driver)
    best_lap = get_quali_laps(session, driver)
    color = get_driver_color(session, driver)
    sectors = ['Sector 1', 'Sector 2', 'Sector 3']
    perfect_times = [result['best_s1'], result['best_s2'], result['best_s3']]
    actual_times = [best_lap['S1'], best_lap['S2'], best_lap['S3']]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sectors,
        y=perfect_times,
        name='Perfect Lap',
        marker=dict(color=COLORS['green']),
        hovertemplate='%{x}<br>Perfect: %{y:.3f}s<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        x=sectors,
        y=actual_times,
        name='Best Actual Lap',
        marker=dict(color=color),
        hovertemplate='%{x}<br>Actual: %{y:.3f}s<extra></extra>'
    ))
    fig.update_layout(
        title=f"{driver} Perfect Lap Analysis",
        xaxis_title="Sector",
        yaxis_title="time (seconds)",
        barmode='group',
        annotations=[
            dict(
                x=0.5,
                y=1.05,
                xref='paper',
                yref='paper',
                text=f"Perfect: {result['perfect_time']}s | Best: {result['best_actual']}s | Gain: {result['time_gain']}s",
                showarrow=False,
                font=dict(size=12, color=COLORS['text_secondary'])
            )
        ]
    )
    fig = apply_f1_theme(fig)
    return fig



                        
def chart_quali_improvement(session, drivers):
    from analyze import get_quali_improvement

    fig = go.Figure()
    used_colors = []

    for driver in drivers:
        result = get_quali_improvement(session, driver)
        if result is None:
            continue

        times = result['times']
        color = get_driver_color(session, driver)
        if color.lower() in [c.lower() for c in used_colors]:
            dash_style = 'dash'
        else:
            dash_style = 'solid'
        used_colors.append(color)

        x_vals = []
        y_vals = []
        for segment in ['Q1', 'Q2', 'Q3']:
            if times[segment] is not None:
                x_vals.append(segment)
                y_vals.append(times[segment])

        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='lines+markers',
            name=driver,
            line=dict(color=color, width=2, dash=dash_style),
            marker=dict(size=8),
            hovertemplate='%{x}: %{y:.3f}s<extra></extra>'
        ))

    fig.update_layout(
        title="Qualifying Progression Q1 - Q2 - Q3",
        xaxis_title="Segment",
        yaxis_title="Best Lap Time (seconds)",
    )
    fig = apply_f1_theme(fig)

    return fig








def chart_circuit_dna(sessions):
    from analyze import get_circuit_dna

    accent_colors = [
        COLORS['red'], COLORS['cyan'], COLORS['yellow'],
        COLORS['green'], COLORS['purple'] ]

    fig = go.Figure()
    for i, session in enumerate(sessions):
        dna = get_circuit_dna(session)
        color = accent_colors[i % len(accent_colors)]

        metrics = {
            'Full Throttle %': (dna['throttle_pct'], 100),
            'Braking %': (dna['braking_pct'], 40),
            'Top Speed': (dna['top_speed'], 380),
            'Corner Speed': (dna['avg_corner_speed'], 200),
            'High Speed %': (dna['high_speed_pct'], 30),
            'Low Speed %': (dna['low_speed_pct'], 50), }

        categories = list(metrics.keys())
        values = [round((v / max_v) * 100, 1) for v, max_v in metrics.values()]
        values_closed = values + [values[0]]
        categories_closed = categories + [categories[0]]
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)

        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill='toself',
            fillcolor=f'rgba({r},{g},{b},0.15)',
            line=dict(color=color, width=2),
            name=f"{dna['circuit']} {dna['year']}"  ))

    fig.update_layout(
        title="Circuit DNA Comparison",
        polar=dict(
            bgcolor=COLORS['paper'],
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor=COLORS['grid'],
                linecolor=COLORS['grid'],
                tickfont=dict(color=COLORS['text_secondary'], size=10) ),
            angularaxis=dict(
                gridcolor=COLORS['grid'],
                linecolor=COLORS['grid'],
                tickfont=dict(color=COLORS['text'], size=13) )),
        showlegend=True,
        height=600,
        width=700 )

    fig = apply_f1_theme(fig)
    return fig





def chart_team_circuit_affinity(affinity_data):
    fig = go.Figure()

    circuit_types = list(affinity_data.keys())
    all_teams = set()
    for teams in affinity_data.values():
        all_teams.update(list(teams.keys())[:5])
    all_teams = list(all_teams)

    team_colors = [
        COLORS['red'], COLORS['cyan'], COLORS['yellow'],
        COLORS['green'], COLORS['purple'], '#FF6B6B',
        '#51CF66', '#FCC419', '#339AF0', '#CC5DE8'  ]

    for i, team in enumerate(all_teams):
        positions = []
        for circuit_type in circuit_types:
            pos = affinity_data[circuit_type].get(team, None)
            positions.append(pos)

        color = TEAM_COLORS.get(team, team_colors[i % len(team_colors)])

        fig.add_trace(go.Bar(
            name=team,
            x=circuit_types,
            y=positions,
            marker=dict(color=color),
            hovertemplate=f'{team}<br>%{{x}}: P%{{y:.1f}}<extra></extra>'
        ))
    fig.update_layout(
        title="Team Performance by Circuit Type",
        xaxis_title="Circuit Type",
        yaxis_title="Average Qualifying Position",
        barmode='group',
        yaxis=dict(autorange='reversed')   )
    all_teams = list(dict.fromkeys(all_teams))
    fig = apply_f1_theme(fig)

    return fig





