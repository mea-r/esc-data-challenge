import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
import numpy as np
from theme import apply_plot_theme

COLOR_PL = '#2e6bff'     
COLOR_EA = '#4cc9f0'      


def plot_fig1_ca_headline(data_dict, date_range, theme=None):
    """
    Figure 1: Structural Break Analysis (Distributions & Divergence).
    Panel A: Distributions of Indexed Current Account (Pre vs Post Feb 2022).
    Panel B: Mean Divergence (Poland - Euro Area) (Pre vs Post Feb 2022).
    """
    if theme is None: theme = {"bg": "#1F1F1F", "paper": "#1F1F1F", "text": "#FAFAFA", "grid": "#374151", "annotation": "#FAFAFA", "shading": "rgba(255, 255, 255, 0.05)"}
    if not data_dict:
        return None
        
    df_pl = data_dict.get("PL_CA_Monthly", pd.DataFrame())
    df_ea = data_dict.get("EA_CA_Monthly", pd.DataFrame())
    
    if df_pl.empty or df_ea.empty:
        return None

    def process_series(df):
        dff = df.copy().sort_values('Date')
        dff['Rolling'] = dff['Value'].rolling(window=12).sum()
        return dff

    pl_full = process_series(df_pl)
    ea_full = process_series(df_ea)
    base_date = pd.Timestamp("2022-01-31")
    
    def get_base_value(df):
        base_row = df.loc[df['Date'] == base_date]
        if base_row.empty: return None
        return base_row['Rolling'].values[0]

    pl_base = get_base_value(pl_full)
    ea_base = get_base_value(ea_full)
    
    if pl_base is None or ea_base is None or pl_base == 0 or ea_base == 0:
        is_indexed = False
        pl_full['Indexed'] = pl_full['Rolling']
        ea_full['Indexed'] = ea_full['Rolling']
        y_title_a = "EUR Millions (12M Sum)"
        y_title_b = "Difference (EUR Millions)"
    else:
        is_indexed = True
        pl_full['Indexed'] = (pl_full['Rolling'] / pl_base) * 100
        ea_full['Indexed'] = (ea_full['Rolling'] / ea_base) * 100
        y_title_a = "Index (Jan 2022 = 100)"
        y_title_b = "Divergence (Index Points)"

    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        
    df_merged = pd.merge(
        pl_full[['Date', 'Indexed']].rename(columns={'Indexed': 'PL'}),
        ea_full[['Date', 'Indexed']].rename(columns={'Indexed': 'EA'}),
        on='Date', how='inner'
    )
    
    mask = (df_merged['Date'] >= start_date) & (df_merged['Date'] <= end_date)
    plot_df = df_merged.loc[mask].copy()
    
    if plot_df.empty:
        return None

    break_date = pd.Timestamp("2022-02-24")
    plot_df['Period'] = plot_df['Date'].apply(lambda x: 'Post-Feb 2022' if x >= break_date else 'Pre-Feb 2022')
    plot_df['Period'] = pd.Categorical(plot_df['Period'], categories=period_order, ordered=True)

    plot_df['Divergence'] = plot_df['PL'] - plot_df['EA']

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("<b>Panel A: Distribution Shift</b>", "<b>Panel B: Mean Divergence (PL - EA)</b>"),
        horizontal_spacing=0.15
    )

    # poland
    fig.add_trace(go.Box(
        y=plot_df[plot_df['Period'] == 'Pre-Feb 2022']['PL'],
        x=['Pre-Feb 2022'] * len(plot_df[plot_df['Period'] == 'Pre-Feb 2022']),
        name="Poland",
        marker_color=COLOR_PL,
        boxpoints=False, # Clean look
        showlegend=True,
        legendgroup="PL"
    ), row=1, col=1)
    
    fig.add_trace(go.Box(
        y=plot_df[plot_df['Period'] == 'Post-Feb 2022']['PL'],
        x=['Post-Feb 2022'] * len(plot_df[plot_df['Period'] == 'Post-Feb 2022']),
        name="Poland",
        marker_color=COLOR_PL,
        boxpoints=False,
        showlegend=False,
        legendgroup="PL"
    ), row=1, col=1)

    # euro area
    fig.add_trace(go.Box(
        y=plot_df[plot_df['Period'] == 'Pre-Feb 2022']['EA'],
        x=['Pre-Feb 2022'] * len(plot_df[plot_df['Period'] == 'Pre-Feb 2022']),
        name="Euro Area",
        marker_color=COLOR_EA,
        boxpoints=False,
        showlegend=True,
        legendgroup="EA"
    ), row=1, col=1)

    fig.add_trace(go.Box(
        y=plot_df[plot_df['Period'] == 'Post-Feb 2022']['EA'],
        x=['Post-Feb 2022'] * len(plot_df[plot_df['Period'] == 'Post-Feb 2022']),
        name="Euro Area",
        marker_color=COLOR_EA,
        boxpoints=False,
        showlegend=False,
        legendgroup="EA"
    ), row=1, col=1)

    stats = plot_df.groupby('Period', observed=True)['Divergence'].agg(['mean', 'sem']).reset_index()
    
    bar_color = '#9CA3AF'

    fig.add_trace(go.Bar(
        x=stats['Period'],
        y=stats['mean'],
        error_y=dict(type='data', array=stats['sem'], visible=True, color=theme['text']),
        name="Divergence (PL - EA)",
        marker_color=bar_color,
        showlegend=False
    ), row=1, col=2)

    fig.update_layout(
        title=dict(
            text="<b>Structural Break Test: Current Account Dynamics</b>",
            x=0.5,
            xanchor='center',
            yanchor='top',
            font=dict(color="#2A3F5F", family="Georgia", size=24, weight=600)
        ),
        font=dict(color="#2A3F5F", family="Georgia", weight=600),
        template="plotly_white",
        plot_bgcolor="#F3F4F6",
        paper_bgcolor="#F3F4F6",
        margin=dict(l=40, r=40, t=70, b=100),

        boxmode='group', 
        autosize=True,
        height=600,
        legend=dict(
            orientation="h",
            yanchor="top",
            # y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=16, color="#2A3F5F", family="Georgia")
        )
    )

    fig.update_yaxes(
        title_font=dict(color="#2A3F5F", family="Georgia", size=18),
        tickfont=dict(color="#2A3F5F", family="Georgia", size=16),
        zeroline=True, zerolinewidth=1,
        tickprefix="<b>", ticksuffix="</b>",
        row=1, col=1
    )
    fig.update_yaxes(
        title_font=dict(color="#2A3F5F", family="Georgia", size=18),
        tickfont=dict(color="#2A3F5F", family="Georgia", size=16),
        zeroline=True, zerolinewidth=1, 
        tickprefix="<b>", ticksuffix="</b>",
        row=1, col=2
    )
    fig.update_xaxes(showgrid=False, color="#2A3F5F", tickfont=dict(size=16, family="Georgia", color="#2A3F5F"), tickprefix="<b>", ticksuffix="</b>", row=1, col=1)
    fig.update_xaxes(showgrid=False, color="#2A3F5F", tickfont=dict(size=16, family="Georgia", color="#2A3F5F"), tickprefix="<b>", ticksuffix="</b>", row=1, col=2)

    return apply_plot_theme(fig)


def plot_fig2_goods_balance(data_dict, date_range, theme=None, overview_mode=False):
    """
    Figure 2: Goods Balance (Poland with Russia and ex-Russia).
    """
    if theme is None: theme = {"bg": "#1F1F1F", "paper": "#1F1F1F", "text": "#FAFAFA", "grid": "#374151", "annotation": "#FAFAFA", "line_total": "#FAFAFA", "shading": "rgba(255, 255, 255, 0.05)"}
    if not data_dict:
        return None

    df_total = data_dict.get("PL_Goods_Total", pd.DataFrame())
    df_russia = data_dict.get("PL_Goods_Russia", pd.DataFrame())

    if df_total.empty or df_russia.empty:
        return None

    df = pd.merge(
        df_total[['Date', 'Value']].rename(columns={'Value': 'Total'}),
        df_russia[['Date', 'Value']].rename(columns={'Value': 'Russia'}),
        on='Date', how='inner'
    )

    if overview_mode:
        start_date, end_date = pd.Timestamp("2020-01-01"), pd.Timestamp("2024-12-31")
    else:
        start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    plot_df = df.loc[mask].copy()
    plot_df['Ex_Russia'] = plot_df['Total'] - plot_df['Russia']

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=plot_df['Date'], y=plot_df['Ex_Russia'],
        name="Ex-Russia",
        marker_color='#4B5563', 
    ))

    fig.add_trace(go.Bar(
        x=plot_df['Date'], y=plot_df['Russia'],
        name="Russia",
        marker_color='#2e6bff', 
    ))



    fig.add_vline(x=pd.Timestamp("2022-02-24"), line_width=3, line_dash="dash", line_color="#2A3F5F")
    
    title_text = "<b>Goods Balance Decomposition</b>" if overview_mode else "<b>Goods Balance Decomposition (Russia vs Ex-Russia)</b>"

    fig.update_layout(
        title=dict(
            text=title_text,
            x=0.5,
            xanchor='center',
            yanchor='top',
            font=dict(color="#2A3F5F", family="Georgia", size=12 if overview_mode else 24, weight=600)
        ),
        font=dict(color="#2A3F5F", family="Georgia", weight=600),
        template="plotly_white",
        plot_bgcolor="#F3F4F6",
        paper_bgcolor="#F3F4F6",
        hovermode="x unified",
        margin=dict(l=10, r=10, t=25, b=10) if overview_mode else dict(l=40, r=40, t=70, b=100),

        xaxis=dict(showgrid=False, color="#2A3F5F", tickfont=dict(size=10 if overview_mode else 16, family="Georgia", color="#2A3F5F"), tickprefix="<b>", ticksuffix="</b>"),
        yaxis=dict(
            title="EUR Millions" if not overview_mode else None,
            color="#2A3F5F",
            zeroline=True, zerolinewidth=2,
            tickfont=dict(size=10 if overview_mode else 16, family="Georgia", color="#2A3F5F"),
            title_font=dict(size=14 if overview_mode else 18, family="Georgia", color="#2A3F5F"),
            tickprefix="<b>", ticksuffix="</b>"
        ),
        barmode='relative',
        bargap=0.2, 
        autosize=True,
        height=220 if overview_mode else 600,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.1 if overview_mode else None, 
            xanchor="center",
            x=0.5,
            font=dict(size=12 if overview_mode else 16, color="#2A3F5F", family="Georgia")
        )
    )
    
    if overview_mode:
        fig.add_vline(x=pd.Timestamp("2022-02-24"), line_width=1, line_dash="solid", line_color="#6B7280")

    return apply_plot_theme(fig)


def plot_fig3_impact_bridge(data_dict, date_range, theme=None):
    """
    Figure 3: Bridge the Impact (CA vs Goods Balance).
    """
    if theme is None: theme = {"bg": "#1F1F1F", "paper": "#1F1F1F", "text": "#FAFAFA", "grid": "#374151", "annotation": "#FAFAFA", "line_total": "#FAFAFA", "shading": "rgba(255, 255, 255, 0.05)"}
    if not data_dict:
        return None

    df_ca_monthly = data_dict.get("PL_CA_Monthly", pd.DataFrame())
    df_goods = data_dict.get("PL_Goods_Total", pd.DataFrame())

    if df_ca_monthly.empty or df_goods.empty:
        return None

    df_ca_monthly['Date'] = pd.to_datetime(df_ca_monthly['Date'])
    df_ca_q = df_ca_monthly.set_index('Date').resample('QE').sum().reset_index()
    df_ca_q = df_ca_q.rename(columns={'Value': 'CA'})
    df_goods = df_goods.rename(columns={'Value': 'Goods'})

    df = pd.merge(df_ca_q, df_goods, on='Date', how='inner')

    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    plot_df = df.loc[mask].copy()

    if plot_df.empty:
        return None

    x = plot_df['Goods']
    y = plot_df['CA']
    r = np.corrcoef(x, y)[0, 1]

    all_vals = pd.concat([plot_df['CA'], plot_df['Goods']])
    y_min, y_max = all_vals.min(), all_vals.max()
    y_range = [y_min * 1.1, y_max * 1.1]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=plot_df['Date'], y=plot_df['CA'],
        name="Current Account",
        line=dict(color=COLOR_PL, width=3)
    ))

    fig.add_trace(go.Scatter(
        x=plot_df['Date'], y=plot_df['Goods'],
        name="Goods Balance",
        line=dict(color=COLOR_EA, width=3)
    ))
    

    fig.update_layout(
        title=dict(
            text="<b>Current Account vs Goods Balance</b>",
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
        margin=dict(l=40, r=40, t=70, b=130),

        autosize=True,
        height=600,
        legend=dict(
            orientation="h",
            yanchor="top",
            # y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=16, color="#2A3F5F", family="Georgia")
        )
    )
    
    fig.add_vline(x=pd.Timestamp("2022-02-24"), line_width=3, line_dash="dash", line_color="#2A3F5F")

    fig.update_yaxes(
        title_text="EUR Millions", 
        title_font=dict(color="#2A3F5F", family="Georgia", size=18),
        tickfont=dict(color="#2A3F5F", family="Georgia", size=16),
        range=y_range,
        tickprefix="<b>", ticksuffix="</b>"
    )
    fig.update_xaxes(showgrid=False, color="#2A3F5F", tickfont=dict(size=16, family="Georgia", color="#2A3F5F"), tickprefix="<b>", ticksuffix="</b>")

    fig.add_annotation(
        text=f"Correlation coefficient: {r:.2f}",
        xref="paper", yref="paper",
        x=0.5, y=-0.25,
        showarrow=False,
        font=dict(family="Georgia", size=10, color="#2A3F5F")
    )

    return apply_plot_theme(fig)


