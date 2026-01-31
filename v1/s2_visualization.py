import plotly.graph_objects as go
import pandas as pd
import math

COLOR_PL = '#2e6bff'
COLOR_EA = '#4cc9f0' 



from theme import apply_plot_theme

def plot_fig1_growth_divergence(df, date_range, theme=None):
    if theme is None: theme = {"bg": "#1F1F1F", "paper": "#1F1F1F", "text": "#FAFAFA", "grid": "#374151", "annotation": "#FAFAFA"}
    
    plot_df = df.copy()
    plot_df['PL_Growth_QoQ'] = plot_df['PL_GDP'].pct_change() * 100
    plot_df = plot_df.dropna(subset=['PL_Growth_QoQ'])
    
    color_hist = COLOR_PL
    color_shock = COLOR_PL
    
    fig = go.Figure()
    
    
    shock_dates = [pd.Timestamp("2022-06-30"), pd.Timestamp("2022-09-30"), pd.Timestamp("2022-12-31")]
    shock_avg = plot_df[plot_df['Date'].isin(shock_dates)]['PL_Growth_QoQ'].mean()

    pre_date = pd.Timestamp("2021-12-31")
    pre_val_series = plot_df[plot_df['Date'] == pre_date]['PL_Growth_QoQ']
    pre_val = pre_val_series.values[0] if not pre_val_series.empty else None

    bin_size = 0.4 
    x_min = math.floor(plot_df['PL_Growth_QoQ'].min())
    x_max = math.ceil(plot_df['PL_Growth_QoQ'].max())
    
    bins = []
    curr = x_min
    while curr <= x_max + bin_size:
        bins.append(curr)
        curr += bin_size
        
    bin_centers = []
    counts = []
    total_points = len(plot_df)
    
    for i in range(len(bins) - 1):
        left = bins[i]
        right = bins[i+1]
        center = (left + right) / 2
        bin_centers.append(center)
        
        if i == len(bins) - 2: 
             c = plot_df[(plot_df['PL_Growth_QoQ'] >= left) & (plot_df['PL_Growth_QoQ'] <= right)].shape[0]
        else:
             c = plot_df[(plot_df['PL_Growth_QoQ'] >= left) & (plot_df['PL_Growth_QoQ'] < right)].shape[0]
        
        density = c / (total_points * bin_size)
        counts.append(density)
    
    colors = [color_hist] * len(counts)
    
    def get_bin_idx(val, edges):
        for i in range(len(edges) - 1):
             if edges[i] <= val < edges[i+1]:
                 return i
        return -1

    if not pd.isna(shock_avg):
        idx = get_bin_idx(shock_avg, bins)
        if 0 <= idx < len(colors):
            colors[idx] = "#FFCC00"
            
    if pre_val is not None:
        idx = get_bin_idx(pre_val, bins)
        if 0 <= idx < len(colors):
            colors[idx] = "#4CC9F0"

    fig.add_trace(go.Bar(
        x=bin_centers,
        y=counts,
        name='Distribution',
        marker_color=colors,
        marker_line=dict(color=theme['text'], width=1),
        opacity=1,
        width=bin_size 
    ))

    fig.add_trace(go.Box(
        x=plot_df['PL_Growth_QoQ'],
        boxpoints='outliers',
        jitter=0,
        pointpos=0,
        orientation='h',
        name='Distribution',
        marker_color='#4B5563',
        line=dict(color=theme['text'], width=1),
        marker=dict(opacity=1, size=5, line=dict(color=theme['text'], width=1), symbol='circle'), 
        xaxis='x',
        yaxis='y2',
        showlegend=False
    ))

    
    band_width = 0.04

    if not pd.isna(shock_avg):
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(symbol='square', size=10, color="#FFCC00", opacity=1),
            name=f"Shock-period mean ({shock_avg:.1f}%)"
        ))

    if pre_val is not None:
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(symbol='square', size=10, color="#4CC9F0", opacity=1),
            name=f"Pre-invasion benchmark ({pre_val:.1f}%)"
        ))

    start_year = plot_df['Date'].min().year
    end_year = plot_df['Date'].max().year

    fig.update_layout(
        title=dict(
            text=f"<b>GDP Growth Distribution</b>",
            x=0.5,
            xanchor='center',
            yanchor='top',
            font=dict(color="#2A3F5F", family="Georgia", size=24, weight=600)
        ),
        font=dict(color="#2A3F5F", family="Georgia", weight=600),
        template="plotly_white",
        plot_bgcolor="#F3F4F6",
        paper_bgcolor="#F3F4F6",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=70, b=100),
        xaxis=dict(
            title="Real GDP Growth (QoQ %)", 
            showgrid=False, 
            color="#2A3F5F",
            zeroline=True, zerolinewidth=1,
            tickfont=dict(size=16, family="Georgia", color="#2A3F5F"),
            title_font=dict(size=18, family="Georgia", color="#2A3F5F"),
            tickprefix="<b>", ticksuffix="</b>",
            title_standoff=25
        ),
        yaxis=dict(
            title="Density", 
            color="#2A3F5F",
            domain=[0, 0.75], 
            showgrid=False,
            tickfont=dict(size=16, family="Georgia", color="#2A3F5F"),
            title_font=dict(size=18, family="Georgia", color="#2A3F5F"),
            tickprefix="<b>", ticksuffix="</b>"
        ),
        yaxis2=dict(
            domain=[0.77, 1],
            showgrid=False,
            visible=False
        ),
        barmode='overlay',
        autosize=True,
        height=600,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(0,0,0,0)',
            font=dict(size=16, color="#2A3F5F", family="Georgia")
        )
    )
    
    return apply_plot_theme(fig)


def plot_fig2_decomposition(df, theme=None):
    if theme is None: theme = {"bg": "#1F1F1F", "paper": "#1F1F1F", "text": "#FAFAFA", "grid": "#374151", "annotation": "#FAFAFA"}
    chart_df = df.copy()
    req_cols = ['Consumption', 'Investment', 'Gov_Spending', 'Exports', 'Imports']
    available = [c for c in req_cols if c in chart_df.columns]

    if not available: return go.Figure()

    p1 = chart_df[(chart_df['Date'] >= '2019-01-01') & (chart_df['Date'] <= '2021-12-31')][available].mean()
    p2 = chart_df[(chart_df['Date'] >= '2022-01-01') & (chart_df['Date'] <= '2024-12-31')][available].mean()

    deltas = {c: p2[c] - p1[c] for c in available if c not in ['Exports', 'Imports']}
    if 'Exports' in available and 'Imports' in available:
        deltas['Net_Exports'] = (p2['Exports'] - p2['Imports']) - (p1['Exports'] - p1['Imports'])
    total = sum(deltas.values())

    fig = go.Figure(go.Waterfall(
        measure=["relative"] * len(deltas) + ["total"],
        x=[k.replace('_', ' ') for k in deltas.keys()] + ["TOTAL SHIFT"],
        y=list(deltas.values()) + [total],
        text=[f"{v / 1000:+.1f}B" for v in list(deltas.values()) + [total]],
        connector={"line": {"color": "#9CA3AF"}},
        increasing={"marker": {"color": COLOR_PL, "line": {"color": theme['text'], "width": 1}}},
        decreasing={"marker": {"color": COLOR_EA, "line": {"color": theme['text'], "width": 1}}},
        totals={"marker": {"color": "#4B5563"}}
    ))
    fig.update_layout(
        title=dict(
            text="<b>Drivers of GDP Change (Volume)</b>",
            x=0.5,
            xanchor='center',
            yanchor='top',
            font=dict(color="#2A3F5F", family="Georgia", size=24, weight=600)
        ),
        font=dict(color="#2A3F5F", family="Georgia", weight=600),
        template="plotly_white",
        paper_bgcolor="#F3F4F6",
        plot_bgcolor="#F3F4F6",
        margin=dict(l=40, r=40, t=70, b=80),
        yaxis=dict(title="EUR Billions (Volume Change)", color="#2A3F5F", tickfont=dict(size=16, family="Georgia", color="#2A3F5F"), title_font=dict(size=18, family="Georgia", color="#2A3F5F"), tickprefix="<b>", ticksuffix="</b>"),
        xaxis=dict(
            color="#2A3F5F", 
            tickfont=dict(size=16, family="Georgia", color="#2A3F5F"), 
            title_font=dict(size=18, family="Georgia", color="#2A3F5F"), 
            tickprefix="<b>", ticksuffix="</b>",
            title_standoff=50
        ),
        autosize=True,
        height=750,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=16, color="#2A3F5F", family="Georgia")
        )
    )
    return apply_plot_theme(fig)


def plot_fig3_animated(df, date_range, theme=None, static_view=False):
    if theme is None: theme = {"bg": "#1F1F1F", "paper": "#1F1F1F", "text": "#FAFAFA", "grid": "#374151", "annotation": "#FAFAFA"}
    mask = (df['Date'] >= pd.Timestamp(date_range[0])) & (df['Date'] <= pd.Timestamp(date_range[1]))
    plot_df = df.loc[mask].copy()

    base_date = pd.Timestamp("2021-12-31")
    base_row = df[df['Date'] == base_date]
    if base_row.empty: base_row = df[df['Date'] < '2022-01-01'].iloc[-1:]
    ea_base = base_row['EA_GDP'].values[0]
    pl_base = base_row['PL_GDP'].values[0]
    plot_df['EA_Index'] = (plot_df['EA_GDP'] / ea_base) * 100
    plot_df['PL_Index'] = (plot_df['PL_GDP'] / pl_base) * 100

    title_text = "<b>Cumulative Real GDP Index (Q4 2021 = 100)</b>" if static_view else "<b>Poland vs Euro Area: Cumulative GDP Growth</b>"

    layout_args = dict(
        title=dict(text=title_text,
                   x=0.5,
                   xanchor='center',
                   yanchor='top',
                   font=dict(color="#2A3F5F", family="Georgia", size=24 if not static_view else 12, weight=600)),
        font=dict(color="#2A3F5F", family="Georgia", weight=600),
        template="plotly_white",
        plot_bgcolor="#F3F4F6",
        paper_bgcolor="#F3F4F6",
        xaxis=dict(range=[pd.Timestamp("2020-01-01"), pd.Timestamp("2024-12-31")] if static_view else [plot_df['Date'].min(), plot_df['Date'].max()], 
                   showgrid=False, color="#2A3F5F", 
                   tickfont=dict(size=16 if not static_view else 10, family="Georgia", color="#2A3F5F"),
                   tickprefix="<b>", ticksuffix="</b>"),
        yaxis=dict(title="Index (Jan-2022 = 100)", range=[85, 115], color="#2A3F5F", 
                   tickfont=dict(size=16 if not static_view else 10, family="Georgia", color="#2A3F5F"),
                   tickprefix="<b>", ticksuffix="</b>"),
        margin=dict(l=40, r=40, t=70, b=100) if not static_view else dict(l=10, r=10, t=25, b=10),
        autosize=True,
        height=600 if not static_view else 220,
        legend=dict(
            orientation="h",
            yanchor="top",
            # y=-0.2 if not static_view else 1.1,
            xanchor="center",
            x=0.5,
            font=dict(size=16, color="#2A3F5F", family="Georgia")
        )
    )

    if static_view:
        fig = go.Figure(layout=go.Layout(**layout_args))
        # Static Traces
        fig.add_trace(go.Scatter(x=plot_df['Date'], y=plot_df['EA_Index'],
                                 mode="lines", line=dict(color=COLOR_EA, width=2), name="Euro Area"))
        fig.add_trace(go.Scatter(x=plot_df['Date'], y=plot_df['PL_Index'],
                                 mode="lines", line=dict(color=COLOR_PL, width=4), name="Poland"))
        
    else:
        fig = go.Figure(
            data=[
                go.Scatter(x=plot_df['Date'], y=plot_df['EA_Index'],
                           mode="lines", line=dict(color=COLOR_EA, width=2), name="Euro Area"),
                go.Scatter(x=plot_df['Date'], y=plot_df['PL_Index'],
                           mode="lines", line=dict(color=COLOR_PL, width=4), name="Poland")
            ],
            layout=go.Layout(
                **layout_args,
                updatemenus=[dict(
                    type="buttons",
                    bgcolor=theme['paper'],
                    bordercolor=theme['text'],
                    font=dict(color=theme['text']),
                    buttons=[dict(label="▶ PLAY SEQUENCE",
                                  method="animate",
                                  args=[None, dict(frame=dict(duration=100, redraw=False), fromcurrent=True)])],
                    x=1,
                    y=1.15,
                    xanchor="right",
                    yanchor="top",
                    showactive=False
                )]
            ),
            frames=[
                go.Frame(
                    data=[
                        go.Scatter(x=plot_df['Date'][:k + 1], y=plot_df['EA_Index'][:k + 1]),
                        go.Scatter(x=plot_df['Date'][:k + 1], y=plot_df['PL_Index'][:k + 1])
                    ]
                )
                for k in range(1, len(plot_df))
            ]
        )
        fig.add_annotation(x=base_date, y=100, text="START", 
                           showarrow=True, arrowhead=1, 
                           ax=-40, ay=-10, 
                           arrowcolor="#000000",
                           font=dict(color=theme['annotation']))

    invasion_date = pd.Timestamp("2021-12-31")
    fig.add_vline(x=invasion_date, line_width=2, line_dash="solid", line_color="#2A3F5F")


    return apply_plot_theme(fig)
