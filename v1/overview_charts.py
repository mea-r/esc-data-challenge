

import importlib
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import textwrap
from typing import Optional, Any




# utilities
def safe_import(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None


def extract_fig(module: Any, candidates):
    if module is None:
        return None
    for name in candidates:
        attr = getattr(module, name, None)
        if attr is None:
            continue
        try:
            if callable(attr):
                fig = attr()
            else:
                fig = attr
            if hasattr(fig, "to_plotly_json"):
                return fig
        except Exception:

            continue
    return None


def make_placeholder(title: str, width: int, height: int, message: str = "Data unavailable"):
    fig = go.Figure()
    fig.add_annotation(text=title, xref="paper", yref="paper", x=0.5, y=0.6, showarrow=False,
                       font=dict(size=14, family="Arial", color="#222"))
    fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.4, showarrow=False,
                       font=dict(size=11, family="Arial", color="#777"))
    fig.update_layout(
        autosize=False,
        width=width,
        height=height,
        margin=dict(l=20, r=20, t=20, b=20),
        template="simple_white",
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def enforce_layout(fig: go.Figure, width: int, height: int, margin=None, legend_horizontal=True):
    if fig is None:
        return None
    try:
        fig.update_layout(autosize=False, width=width, height=height)
        if margin is None:
            margin = dict(l=30, r=20, t=30, b=30)
        fig.update_layout(margin=margin, font=dict(size=10))
        if legend_horizontal:
            fig.update_layout(legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.22,
                xanchor='center',
                x=0.5,
                font=dict(size=10)
            ))
        try:
            fig.update_xaxes(showgrid=False)
        except Exception:
            pass
    except Exception:
        pass
    return fig

MODULE_MAP = {
    "s1": "s1.fig1",
    "s2": "s2_visualization",
    "s3": "s3_visualization",
    "s4": "s4_visualization",
}

FIG_NAME_CANDIDATES = [
    "cumulative_gdp_fig",
    "fig_cumulative_gdp",
    "fig3",
    "get_cumulative_gdp_fig",
    "get_fig",
    "FIG",
    "fig",
    "figure",
    "get_figure",
    "main_figure",
    "plot_fig3_animated"
]

ENERGY_CANDIDATES = [
    "energy_imports_fig",
    "fig_energy",
    "fig1",
    "get_energy_fig",
    "energy_fig",
    "plot_price_stability"
]

INFLATION_CANDIDATES = [
    "inflation_composition_fig",
    "fig_inflation",
    "fig2",
    "get_inflation_fig",
    "inflation_fig",
    "get_inflation_data"
]

GOODS_CANDIDATES = [
    "goods_balance_fig",
    "fig_goods",
    "fig6",
    "get_goods_fig",
    "goods_fig",
    "plot_fig2_goods_balance"
]

KPI_CANDIDATES = [
    "SUMMARY_KPIS",
    "kpis",
    "get_kpis",
    "fetch_kpis"
]

# sizing
HERO_W, HERO_H = 760, 300
SMALL_W, SMALL_H = 420, 240
GOODS_W, GOODS_H = 760, 260

def render_overview():
    # load modules & figures
    s1 = safe_import(MODULE_MAP.get("s1"))
    s2 = safe_import(MODULE_MAP.get("s2"))
    s3 = safe_import(MODULE_MAP.get("s3"))
    s4 = safe_import(MODULE_MAP.get("s4"))

    from theme import get_theme
    from data_fetcher import get_growth_data, get_s3_data, fetch_ecb_data
    from datetime import datetime
    import numpy as np
    
    current_theme = get_theme("light") 
    
    min_date = datetime(2018, 1, 1)
    max_date = datetime(2025, 12, 31)
    date_range = (min_date, max_date)
        
    from s2_visualization import plot_fig3_animated
    from s2_visualization import plot_fig3_animated
    from s1.fig1 import plot_price_stability, get_data as get_energy_data, rebase as rebase_energy, get_unit_value
    from s1.fig2_5 import plot_hicp_contribution
    from s3_visualization import plot_fig2_goods_balance
    from s2_visualization import plot_fig3_animated
    from s1.fig1 import plot_price_stability
    from s1.fig2_5 import plot_hicp_contribution
    from s3_visualization import plot_fig2_goods_balance
    
    df_growth = get_growth_data()
    hero_fig = plot_fig3_animated(df_growth, date_range, current_theme, static_view=True)
    
    def plot_energy_overview():
        try:
            vol_file = "data/s1fig1/Gas_Vol.csv"
            val_file = "data/s1fig1/Gas_Val.csv"
            
            df_Val = get_energy_data(val_file)
            df_Vol = get_energy_data(vol_file)
            
            df_Val = rebase_energy(df_Val, "2022-January")
            df_Vol = rebase_energy(df_Vol, "2022-January")
            df_unit = get_unit_value(df_Val, df_Vol)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_Val["Date"], y=df_Val["Value"],
                mode='lines',
                name='Value',
                line=dict(color="#2E6BFF", width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=df_Vol["Date"], y=df_Vol["Value"],
                mode='lines',
                name='Volume',
                line=dict(color="#4CC9F0", width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=df_unit["Date"], y=df_unit["Value"],
                mode='lines',
                name='Unit Price',
                line=dict(color="#FFCC00", width=2)
            ))
            
            fig.update_layout(
                template="plotly_white",
                title=dict(text="<b>Energy Import Price vs Volume</b>", x=0.5, xanchor='center', y=0.95),
                plot_bgcolor="#F3F4F6",
                paper_bgcolor="#F3F4F6",
                yaxis=dict(
                    title=dict(text="<b>Index (Jan 2022=100)</b>", font=dict(color="#2A3F5F", size=10)),
                    showgrid=False, 
                    gridcolor='#E5E7EB', 
                    zeroline=True, 
                    zerolinecolor='#E5E7EB',
                    tickfont=dict(family="Georgia", color="#2A3F5F", weight=600),
                    tickprefix="<b>", ticksuffix="</b>"
                ),
                xaxis=dict(
                    showgrid=False,
                    tickfont=dict(family="Georgia", color="#2A3F5F", weight=600),
                    tickprefix="<b>", ticksuffix="</b>"
                ),
                legend=dict(
                    font=dict(family="Georgia", color="#2A3F5F", weight=600)
                ),
                margin=dict(l=0, r=0, t=50, b=0)
            )
            return fig
            
        except Exception as e:
            print(f"Energy overview error: {e}")
            return None

    energy_fig = plot_energy_overview()
    
    s3_data = get_s3_data()
    goods_fig = plot_fig2_goods_balance(s3_data, date_range, current_theme, overview_mode=True)
    
    inflation_fig = plot_hicp_contribution()
    if not inflation_fig:
         inflation_fig = make_placeholder("Poland Inflation Composition", SMALL_W, SMALL_H, message="(Data unavailable)")

    pl_gdp_pre_val, pl_gdp_shock_val, peak_inflation_val = "N/A", "N/A", "N/A"
    if not df_growth.empty:
        mask_pre = (df_growth['Date'] >= '2019-01-01') & (df_growth['Date'] < '2022-01-01')
        mask_shock = (df_growth['Date'] >= '2022-04-01') & (df_growth['Date'] <= '2022-12-31')
        
        val_pre = df_growth[mask_pre]['PL_GDP'].pct_change().mean() * 100
        val_shock = df_growth[mask_shock]['PL_GDP'].pct_change().mean() * 100
        
        pl_gdp_pre_val = f"{val_pre:.2f}%"
        pl_gdp_shock_val = f"{val_shock:.2f}%"
        
    pl_hicp_pre_val, pl_hicp_shock_val = "N/A", "N/A"
    try:
        from s1.fig2_5 import get_data as get_hicp_data
        _, _, df_hicp = get_hicp_data()
        
        if not df_hicp.empty:
            val_col = df_hicp.columns[2] 
            
            mask_pre_infl = (df_hicp['DATE'] >= '2021-10-01') & (df_hicp['DATE'] <= '2021-12-31')
            val_pre_infl = df_hicp.loc[mask_pre_infl, val_col].mean()
            
            mask_shock_infl = (df_hicp['DATE'] >= '2022-04-01') & (df_hicp['DATE'] <= '2022-12-31')
            val_shock_infl = df_hicp.loc[mask_shock_infl, val_col].mean()
            
            pl_hicp_pre_val = f"{val_pre_infl:.1f}%"
            pl_hicp_shock_val = f"{val_shock_infl:.1f}%"
    except Exception as e:
        print(f"Inflation KPI error: {e}")

    pl_tot_pre_val, pl_tot_shock_val = "N/A", "N/A"
    try:
        key_exp_val = "Q.Y.PL.W1.S1.S1.D.P6._Z._Z._Z.EUR.V.N"
        key_imp_val = "Q.Y.PL.W1.S1.S1.C.P7._Z._Z._Z.EUR.V.N"
        key_exp_vol = "Q.Y.PL.W1.S1.S1.D.P6._Z._Z._Z.EUR.LR.N"
        key_imp_vol = "Q.Y.PL.W1.S1.S1.C.P7._Z._Z._Z.EUR.LR.N"
        
        df_exp_v = fetch_ecb_data("data", "MNA", key_exp_val)
        df_imp_v = fetch_ecb_data("data", "MNA", key_imp_val)
        df_exp_l = fetch_ecb_data("data", "MNA", key_exp_vol)
        df_imp_l = fetch_ecb_data("data", "MNA", key_imp_vol)
        
        if not (df_exp_v.empty or df_imp_v.empty or df_exp_l.empty or df_imp_l.empty):
             df_tot = pd.merge(df_exp_v.rename(columns={'Value': 'Exp_V'}), df_imp_v.rename(columns={'Value': 'Imp_V'}), on='Date')
             df_tot = pd.merge(df_tot, df_exp_l.rename(columns={'Value': 'Exp_L'}), on='Date')
             df_tot = pd.merge(df_tot, df_imp_l.rename(columns={'Value': 'Imp_L'}), on='Date')
             
             df_tot['Exp_P'] = df_tot['Exp_V'] / df_tot['Exp_L']
             df_tot['Imp_P'] = df_tot['Imp_V'] / df_tot['Imp_L']
             df_tot['ToT'] = (df_tot['Exp_P'] / df_tot['Imp_P']) * 100
             
             mask_pre_tot = (df_tot['Date'] == '2021-12-31')
             mask_shock_tot = (df_tot['Date'] >= '2022-04-01') & (df_tot['Date'] <= '2022-12-31')
             
             val_pre_tot = df_tot.loc[mask_pre_tot, 'ToT'].mean()
             val_shock_tot = df_tot.loc[mask_shock_tot, 'ToT'].mean()
             
             pl_tot_pre_val = f"{val_pre_tot:.1f}"
             pl_tot_shock_val = f"{val_shock_tot:.1f}"
             
    except Exception as e:
        print(f"ToT KPI error: {e}")

    summary_kpis = {
        "gdp_pre": pl_gdp_pre_val,
        "gdp_shock": pl_gdp_shock_val,
        "infl_pre": pl_hicp_pre_val,
        "infl_shock": pl_hicp_shock_val,
        "tot_pre": pl_tot_pre_val,
        "tot_shock": pl_tot_shock_val
    } 

    margin_tight = dict(l=30, r=20, t=30, b=40) # b=40 for legend space
    
    hero_fig = enforce_layout(hero_fig, HERO_W, HERO_H, margin=margin_tight)
    energy_fig = enforce_layout(energy_fig, SMALL_W, SMALL_H, margin=margin_tight)
    inflation_fig = enforce_layout(inflation_fig, SMALL_W, SMALL_H, margin=margin_tight)
    goods_fig = enforce_layout(goods_fig, GOODS_W, GOODS_H, margin=margin_tight)

    st.markdown("""
        <style>
               .block-container {
                    padding-top: 0rem !important;
                    padding-bottom: 8rem !important;
                }
                header {visibility: hidden;}
                [data-testid="stAppViewContainer"] > .main {
                    padding-top: 0rem !important;
                }
                h3 {
                    margin-top: 0 !important;
                    padding-top: 0 !important;
                }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("### MACROECONOMIC IMPACT OF THE 2022 INVASION")

    GRID_H = 260
        
    GRID_W = 380
    
    grid_margin = dict(l=45, r=10, t=25, b=20)
    
    def style_fig(fig, line_date="2022-02-24"):
        if fig is None: return None
        
        fig = enforce_layout(fig, GRID_W, GRID_H, margin=grid_margin)
        
        fig.layout.shapes = [s for s in fig.layout.shapes if not (hasattr(s, 'type') and s.type == 'line' and s.x0 == s.x1)]
        fig.layout.shapes = [] 
        
        fig.layout.annotations = [a for a in fig.layout.annotations if "Feb 2022" not in a.text and "INVASION" not in a.text and "After the 2022 shock" not in a.text]

        fig.add_vline(x=pd.Timestamp(line_date), line_width=3, line_dash="dash", line_color="#2A3F5F")

        fig.update_layout(
            font=dict(family="Georgia", size=10, color="#333"),
            title_font=dict(family="Georgia", size=12, color="#2A3F5F"),
            legend=dict(
                font=dict(family="Georgia", size=10),
                orientation='h',
                yanchor='top',
                y=-0.15, 
                xanchor='center',
                x=0.5
            ),
            xaxis=dict(tickfont=dict(family="Georgia", size=8), title_font=dict(family="Georgia", size=10)),
            yaxis=dict(tickfont=dict(family="Georgia", size=8), title_font=dict(family="Georgia", size=10))
        )
        return fig

    hero_fig = style_fig(hero_fig, line_date="2021-12-31")
    energy_fig = style_fig(energy_fig)
    inflation_fig = style_fig(inflation_fig)
    if inflation_fig:
        inflation_fig.update_layout(title_y=0.96) 

    goods_fig = style_fig(goods_fig)
    if goods_fig:
        goods_fig.update_yaxes(nticks=6, title=dict(text="EUR Millions", font=dict(size=10, color="#2A3F5F")))
        goods_fig.update_layout(margin=dict(l=35))

    c1, c2, c3 = st.columns(3)
    
    with c1:
        # block 1: Context & research question
        st.markdown(f"""
        <div style="height: {GRID_H}px; display: flex; flex-direction: column; justify-content: start; border-left: 2px solid #eee; padding-left: 15px; padding-right: 15px;">
             <h4 style="font-family: 'Georgia', serif; font-size: 16px; font-weight: bold; margin-bottom: 2px; color: #2A3F5F;">Context & Research Question</h4>
            <div style="font-size: 13px; color: #333; line-height: 1.4; font-family: 'Georgia', serif;">
            The 2022 invasion triggered a price-led energy shock that disrupted inflation and external balances across Europe.
            <br><br>
            Did Russia’s full-scale invasion of Ukraine (24 Feb 2022) coincide with discernible changes in Poland’s key macroeconomic indicators, and did Poland’s response diverge from the euro area benchmark?
            </div>
            <div style="margin-top: 20px; font-size: 11px; color: #888; font-family: 'Georgia', serif; font-style: italic;">
            Data sources: Eurostat, BIS
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        # block 2: Output response
        st.plotly_chart(hero_fig, width="stretch", config={'displayModeBar': False})
        st.markdown('<div style="margin-top: -10px; font-size: 11px; color: #555; font-family: \'Georgia\', serif;">After an initial shock and a negative growth rate, Poland’s cumulative real GDP rises above the euro area benchmark.</div>', unsafe_allow_html=True)
        
    with c3:
        # block 3: Energy price transmission
        st.plotly_chart(energy_fig, width="stretch", config={'displayModeBar': False}, theme=None)
        st.markdown('<div style="margin-top: -10px; font-size: 11px; color: #555; font-family: \'Georgia\', serif;">The post-invasion rise in the energy import bill is driven primarily by higher unit prices rather than volumes.</div>', unsafe_allow_html=True)

    st.write("")

    # ROW 2
    c4, c5, c6 = st.columns(3)
    
    with c4:
        # block 4: Inflation dynamics
        st.plotly_chart(inflation_fig, width="stretch", config={'displayModeBar': False})
        st.markdown('<div style="margin-top: -10px; font-size: 11px; color: #555; font-family: \'Georgia\', serif;">Inflation initially reflects energy prices but remains elevated as food and core components contribute.</div>', unsafe_allow_html=True)
    
    with c5:
        # block 5: External adjustment
        st.plotly_chart(goods_fig, width="stretch", config={'displayModeBar': False})
        st.markdown('<div style="margin-top: -10px; font-size: 11px; color: #555; font-family: \'Georgia\', serif;">The initial goods-balance deterioration is closely linked to Russia-related trade, while later movements reflect broader ex-Russia dynamics.</div>', unsafe_allow_html=True)
        
    kpi_template = (
        '<div style="height: {GRID_H}px; display: flex; flex-direction: column; justify-content: flex-start; border-left: 2px solid #eee; padding-left: 15px; padding-top: 5px; font-family: \'Georgia\', serif;">\n'
        '<h4 style="font-size: 16px; font-weight: bold; margin-bottom: 2px; margin-top: 0; color: #2A3F5F;">Key Indicators</h4>\n'
        '\n'
        '<!-- Row 1: GDP -->\n'
        '<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; border: 1px solid #e0e0e0; padding: 8px; border-radius: 6px; background-color: #F3F4F6;">\n'
        '<!-- Metrics -->\n'
        '<div style="display: flex; gap: 20px;">\n'
        '<div>\n'
        '<div style="font-size: 9px; color: #666; text-transform: uppercase;">GDP (Pre)</div>\n'
        '<div style="font-size: 24px; font-weight: bold; color: #2A3F5F; line-height: 1;">{gdp_pre}</div>\n'
        '</div>\n'
        '<div>\n'
        '<div style="font-size: 9px; color: #666; text-transform: uppercase;">GDP (Shock)</div>\n'
        '<div style="font-size: 24px; font-weight: bold; color: #2A3F5F; line-height: 1;">{gdp_shock}</div>\n'
        '</div>\n'
        '</div>\n'
        '<!-- Note -->\n'
        '<div style="font-size: 10px; color: #555; background: transparent; padding: 4px; border-radius: 4px; width: 110px; text-align: right; line-height: 1.2;">\n'
        'Avg QoQ growth<br>2019–21 vs Q2–Q4 \'22\n'
        '</div>\n'
        '</div>\n'
        '\n'
        '<!-- Row 2: Inflation -->\n'
        '<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; border: 1px solid #e0e0e0; padding: 8px; border-radius: 6px; background-color: #F3F4F6;">\n'
        '<!-- Metrics -->\n'
        '<div style="display: flex; gap: 20px;">\n'
        '<div>\n'
        '<div style="font-size: 9px; color: #666; text-transform: uppercase;">Infl (Pre)</div>\n'
        '<div style="font-size: 24px; font-weight: bold; color: #2A3F5F; line-height: 1;">{infl_pre}</div>\n'
        '</div>\n'
        '<div>\n'
        '<div style="font-size: 9px; color: #666; text-transform: uppercase;">Infl (Shock)</div>\n'
        '<div style="font-size: 24px; font-weight: bold; color: #2A3F5F; line-height: 1;">{infl_shock}</div>\n'
        '</div>\n'
        '</div>\n'
        '<!-- Note -->\n'
        '<div style="font-size: 10px; color: #555; background: transparent; padding: 4px; border-radius: 4px; width: 110px; text-align: right; line-height: 1.2;">\n'
        'Headline HICP<br>Q4 \'21 vs Q2–Q4 \'22\n'
        '</div>\n'
        '</div>\n'
        '\n'
        '<!-- Row 3: ToT -->\n'
        '<div style="display: flex; align-items: center; justify-content: space-between; border: 1px solid #e0e0e0; padding: 8px; border-radius: 6px; background-color: #F3F4F6;">\n'
        '<!-- Metrics -->\n'
        '<div style="display: flex; gap: 20px;">\n'
        '<div>\n'
        '<div style="font-size: 9px; color: #666; text-transform: uppercase;">ToT (Pre)</div>\n'
        '<div style="font-size: 24px; font-weight: bold; color: #2A3F5F; line-height: 1;">{tot_pre}</div>\n'
        '</div>\n'
        '<div>\n'
        '<div style="font-size: 9px; color: #666; text-transform: uppercase;">ToT (Shock)</div>\n'
        '<div style="font-size: 24px; font-weight: bold; color: #2A3F5F; line-height: 1;">{tot_shock}</div>\n'
        '</div>\n'
        '</div>\n'
        '<!-- Note -->\n'
        '<div style="font-size: 10px; color: #555; background: transparent; padding: 4px; border-radius: 4px; width: 110px; text-align: right; line-height: 1.2;">\n'
        'Exp P / Imp P<br>Q4 \'21 vs Q2–Q4 \'22\n'
        '</div>\n'
        '</div>\n'
        '<div style="margin-top: 10px; font-size: 10px; color: #666; font-style: italic;">\n'
        '* Infl = Inflation, ToT = Terms of Trade\n'
        '</div>\n'
        '</div>'
    )
    
    kpi_html = kpi_template.format(
        GRID_H=GRID_H,
        text_color=current_theme['text'],
        accent_color=current_theme['accent'],
        gdp_pre=summary_kpis['gdp_pre'],
        gdp_shock=summary_kpis['gdp_shock'],
        infl_pre=summary_kpis['infl_pre'],
        infl_shock=summary_kpis['infl_shock'],
        tot_pre=summary_kpis['tot_pre'],
        tot_shock=summary_kpis['tot_shock']
    )

    with c6:
        # block 6: Key indicators
        st.markdown(kpi_html, unsafe_allow_html=True)

    st.write("")

