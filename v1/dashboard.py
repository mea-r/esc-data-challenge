import streamlit as st
import pandas as pd
import requests
import io
from s2_visualization import plot_fig1_growth_divergence, plot_fig2_decomposition, plot_fig3_animated
from s3_visualization import plot_fig1_ca_headline, plot_fig2_goods_balance, plot_fig3_impact_bridge
from s1.fig1 import plot_price_stability

from s1.fig2 import plot_inflation_comparison
from s1.fig3 import plot_exchange_rate_inflation
from s1.fig2_5 import plot_hicp_contribution
from data_fetcher import get_growth_data, get_current_account_data, get_s3_data
from datetime import datetime
from theme import get_theme, COLORS

st.set_page_config(
    page_title="Macro Monitor: Poland",
    page_icon="🇵🇱",
    layout="wide",
    initial_sidebar_state="collapsed" 
)

def main():
    page = st.radio(
        "NAVIGATE",
        ["OVERVIEW", "DETAILED ANALYSIS"],
        horizontal=True,
        label_visibility="collapsed",
        key="nav"
    )

    current_theme = get_theme("light")
    theme_mode = "Light"

    min_date = datetime(2018, 1, 1)
    max_date = datetime(2025, 12, 31)
    date_range = (min_date, max_date)

    def figure_header(text):
        st.markdown(f'''
            <div class="geo-text" style="
                background-color: {current_theme['paper']};
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 10px;
                color: {current_theme['text']};
            ">
                <p style="
                    font-family: Georgia, serif;
                    font-weight: 600;
                    font-size: 18px;
                    margin: 0;
                ">{text}</p>
            </div>
        ''', unsafe_allow_html=True)

    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        .stApp, p, li, a, .stMetric, .stMarkdown, h1, h2, h3, h4, h5, h6 {{
            font-family: 'Inter', sans-serif !important;
            line-height: 1.6 !important;
        }}

        .geo-text, .geo-text p {{
            font-family: 'Georgia', serif !important;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Georgia', serif !important;
        }}

        .stApp {{
            background-color: {current_theme['bg']};
            color: {current_theme['text']};
        }}

        header[data-testid="stHeader"] {{
            background-color: {current_theme['bg']} !important;
        }}
        div[data-testid="stDecoration"] {{
            background-image: none;
            background-color: {current_theme['bg']};
        }}

        h1, .stMarkdown h1, .stTitle h1, div[data-testid="stMarkdownContainer"] h1 {{
            font-weight: 700;
            padding-bottom: 20px;
            margin-bottom: 40px !important; 
            letter-spacing: -1px;
            color: {current_theme['text']} !important;
            border-left: 6px solid {current_theme['accent']} !important;
            padding-left: 30px !important;
            text-transform: uppercase;
            font-size: 28px !important;
        }}

        h2, h3 {{
            font-weight: 700;
            color: {current_theme['text']} !important;
            letter-spacing: -0.5px;
            text-transform: uppercase;
            margin-top: 30px !important;
            margin-bottom: 15px !important;
        }}
        
        div[data-testid="stMetric"] {{
            background-color: {current_theme['card_bg']};
            box-shadow: { "0 2px 5px rgba(0,0,0,0.05)" if theme_mode == "Light" else "none" };
            border: { "1px solid " + current_theme['grid'] if theme_mode == "Dark" else "none" };
            border-radius: 6px;
            padding: 24px;
            min-height: 140px; 
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        div[data-testid="stMetricLabel"] p {{
            font-family: 'Space Mono', monospace !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            color: {current_theme['subtext']} !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        div[data-testid="stMetricValue"] div {{
            font-family: 'Inter', sans-serif !important;
            font-size: 36px !important;
            font-weight: 700 !important;
            color: {current_theme['text']} !important;
        }}

        section[data-testid="stSidebar"] {{
            display: none !important;
        }}

        div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {{
            background-color: {current_theme['accent']} !important;
            border-color: {current_theme['accent']} !important;
        }}
        
        div[data-testid="stRadio"] label p,
        div[data-testid="stRadio"] label div,
        div[data-testid="stRadio"] label span,
        div[data-testid="stRadio"] label li {{
            font-family: 'Inter', sans-serif !important;
            font-size: 13px !important;
            font-weight: 400 !important;
            color: {current_theme['text']} !important;
        }}

        .stPlotlyChart {{
            background-color: {current_theme['paper']} !important;
            border-radius: 6px;
            height: auto !important;
            overflow: visible !important;
        }}

        button {{
            background-color: {current_theme['card_bg']} !important;
            border: 1px solid {current_theme['grid']} !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
            border-radius: 4px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            color: {current_theme['text']} !important;
            font-size: 12px !important;
        }}
        button:hover {{
            border-color: {current_theme['accent']} !important;
            color: {current_theme['accent']} !important;
        }}

        div[data-testid="stSlider"] div {{
            color: {current_theme['subtext']} !important;
            font-family: 'Inter', sans-serif !important;
        }}
        
        .stAlert {{
            background-color: {current_theme['card_bg']};
            color: {current_theme['text']};
            border: 1px solid {current_theme['grid']};
            border-radius: 6px;
            font-family: 'Inter', sans-serif !important;
        }}
        
        div[data-testid="stToggle"] label {{
            font-family: 'Space Mono', monospace !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            color: {current_theme['text']} !important;
        }}
        
        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 100px !important;
        }}
        
        div[data-testid="stRadio"] {{
            position: fixed !important;
            bottom: 30px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: auto !important;
            background-color: {current_theme['card_bg']} !important;
            border-radius: 50px !important;
            border: 1px solid {current_theme['grid']} !important;
            z-index: 999999 !important;
            padding: 6px !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
        }}
        
        div[data-testid="stRadio"] div[role="radiogroup"] {{
            display: flex !important;
            justify-content: center !important;
            gap: 4px !important;
        }}
        
        div[data-testid="stRadio"] label > div:first-child {{
            display: none !important;
        }}
        
        div[data-testid="stRadio"] label {{
            background-color: transparent !important;
            border-radius: 40px !important;
            padding: 8px 16px !important;
            margin: 0 !important;
            border: none !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
        }}

        div[data-testid="stRadio"] label p {{
            font-family: 'Inter', sans-serif !important;
            font-size: 13px !important;
            font-weight: 400 !important;
            color: {current_theme['subtext']} !important;
            text-transform: none !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
        }}
        
        div[data-testid="stRadio"] label:has(input:checked) {{
            background-color: {current_theme['grid']} !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
        }}

        div[data-testid="stRadio"] label:has(input:checked) p {{
            color: {current_theme['text']} !important;
            font-weight: 600 !important;
        }}
        
        div[data-testid="stRadio"] label:hover {{
            background-color: {current_theme['bg']} !important;
        }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


    if page == "OVERVIEW":
        from overview_charts import render_overview
        render_overview()

    elif page == "DETAILED ANALYSIS":
        st.title("1. PRICE STABILITY")
        
        vol_file = "data/s1fig1/Gas_Vol.csv"
        val_file = "data/s1fig1/Gas_Val.csv"
        
        fig = plot_price_stability(vol_file, val_file, current_theme)
        
        if fig:
            col_text, col_chart = st.columns([1, 3])
            with col_text:
                figure_header("Figure 1")
                st.markdown(f"""
                <div class="geo-text" style="
                    background-color: {current_theme['paper']};
                    padding: 20px;
                    border-radius: 6px;
                    color: {current_theme['text']};
                    margin-top: 0px;
                ">
                    <p style="margin: 0; font-size: 14px;"><strong>Petroleum Imports – Value vs Volume (Euro Area)</strong><br><br>In months immediately following the invasion, import values rise sharply and reach a clear peak in mid-2022, while import volumes increase more gradually and never display a comparable spike. In parallel, the implied unit price rises steeply through 2022 and then reverses into 2023. The joint pattern is consistent with a terms-of-trade shock in which the import bill is driven mainly by higher energy prices rather than by a large expansion in imported quantities.</p>
                </div>
                """, unsafe_allow_html=True)
            with col_chart:
                st.plotly_chart(fig, config={'displayModeBar': False, 'responsive': True}, theme=None)
        else:
            st.error(f"DATA MISSING: Please ensure '{vol_file}' and '{val_file}' are in the 'data/' directory.")

        st.markdown("###")
        

        try:
            fig3 = plot_inflation_comparison()
            if fig3:
                col_text, col_chart = st.columns([1, 3])
                with col_text:
                    figure_header("Figure 2")
                    st.markdown(f"""
                <div class="geo-text" style="
                    background-color: {current_theme['paper']};
                    padding: 20px;
                    border-radius: 6px;
                    color: {current_theme['text']};
                    margin-top: 0px;
                ">
                    <p style="margin: 0; font-size: 14px;"><strong>Headline HICP YoY Contributions (Poland vs Euro Area)</strong><br><br>In both economies, the post-invasion surge is initially led by energy, consistent with the energy-price shock documented earlier. However, the composition and persistence differ materially. Poland exhibits a substantially larger inflation build up, with energy and food contributions rising more sharply and with core inflation increasing to a much higher peak.</p>
                </div>
                """, unsafe_allow_html=True)
                with col_chart:
                    st.plotly_chart(fig3, config={'displayModeBar': False, 'responsive': True})
            else:
                 pass
        except Exception as e:
            st.warning(f"Could not load Inflation Comparison Chart: {e}")

        st.markdown("###")

        try:
            fig4 = plot_exchange_rate_inflation()
            if fig4:
                 col_text, col_chart = st.columns([1, 3])
                 with col_text:
                    figure_header("Figure 3")
                    st.markdown(f"""
                <div class="geo-text" style="
                    background-color: {current_theme['paper']};
                    padding: 20px;
                    border-radius: 6px;
                    color: {current_theme['text']};
                    margin-top: 0px;
                ">
                    <p style="margin: 0; font-size: 14px;"><strong>Exchange Rate and Energy Inflation</strong><br><br>The figure is consistent with an imported-inflation mechanism in which the initial energy shock is reinforced by currency movements. In the months following February 2022, Poland’s NEER weakens relative to its baseline while energy inflation rises sharply and reaches a pronounced peak during 2022. A depreciation of the effective exchange rate increases the domestic-currency cost of energy imports, raising retail energy prices directly and intensifying cost pressures for firms.</p>
                </div>
                """, unsafe_allow_html=True)
                 with col_chart:
                    st.plotly_chart(fig4, config={'displayModeBar': False, 'responsive': True})
        except Exception as e:
             st.warning(f"Could not load Exchange Rate Chart: {e}")

        st.markdown("---")

        st.title("2. ECONOMIC GROWTH")

        df = get_growth_data()

        if df.empty:
            st.error("CONNECTION ERROR: UNABLE TO FETCH ECB DATA.")
        else:
            col_text, col_chart = st.columns([1, 3])
            with col_text:
                figure_header("Figure 4")
                st.markdown(f"""
                <div class="geo-text" style="
                    background-color: {current_theme['paper']};
                    padding: 20px;
                    border-radius: 6px;
                    color: {current_theme['text']};
                    margin-top: 0px;
                ">
                    <p style="margin: 0 0 12px 0; font-size: 14px; line-height: 1.5;">
                        The central result is a clear downward shift in average growth. The shock-period mean is approximately −0.7%, compared with a pre-invasion benchmark of roughly 2.0%. This difference implies that, in the quarters closest to the invasion, Poland moved from an environment consistent with quick expansion to one in which the typical quarterly outcome was contractionary.
                    </p>
                    <p style="margin: 0; font-size: 12px; color: #888; line-height: 1.4;">
                        <strong>Methodology:</strong><br>
                        Quarterly real GDP growth is computed as quarter-on-quarter percentage changes in Poland’s real GDP over the full available sample. The histogram shows the empirical distribution of growth outcomes, with a boxplot summarizing dispersion. Vertical reference lines mark the average growth rate during the immediate post-invasion shock window (2022Q2–2022Q4) and the pre-invasion benchmark (2021Q4).
                    </p>
                </div>
                """, unsafe_allow_html=True)
            with col_chart:
                st.plotly_chart(plot_fig1_growth_divergence(df, date_range, current_theme), 
                            config={'displayModeBar': False, 'responsive': True})

            st.markdown("###")
            col_text, col_chart = st.columns([1, 3])
            with col_text:
                figure_header("Figure 5")
                st.markdown(f"""
                <div class="geo-text" style="
                    background-color: {current_theme['paper']};
                    padding: 20px;
                    border-radius: 6px;
                    color: {current_theme['text']};
                    margin-top: 0px; 
                ">
                    <p style="margin: 0 0 12px 0; font-size: 14px; line-height: 1.5;">
                        Poland’s cumulative real GDP index rises above the euro area path and the distance widens over time. The invasion shock, while disruptive in the short run, did not push Poland onto a persistently lower relative output path; instead, the medium-run pattern is consistent with a faster return to expansion and stronger cumulative growth than in the euro benchmark.
                    </p>
                    <p style="margin: 0; font-size: 12px; color: #888; line-height: 1.4;">
                        <strong>Methodology:</strong><br>
                        Real GDP levels for Poland and the euro area are converted into an index by rebasing both series to Q4 2021 = 100 (using the 2021-12-31 observation as the base, or the latest pre-2022 observation if missing). The chart then plots the indexed paths over time to compare cumulative output performance, with a vertical reference line at the base quarter.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            with col_chart:
                st.plotly_chart(plot_fig3_animated(df, date_range, current_theme), 
                            config={'displayModeBar': False, 'responsive': True})

            st.markdown("###")
            col_text, col_chart = st.columns([1, 3])
            with col_text:
                figure_header("Figure 6")
                st.markdown(f"""
                <div class="geo-text" style="
                    background-color: {current_theme['paper']};
                    padding: 20px;
                    border-radius: 6px;
                    color: {current_theme['text']};
                    margin-top: 0px; 
                ">
                    <p style="margin: 0 0 12px 0; font-size: 14px; line-height: 1.5;">
                        The decomposition compares average levels across two multi-year windows and shows positive contributions from private consumption, investment, government spending, and net exports. The implication is that Poland’s post-invasion expansion is not consistent with a single compensating factor masking weakness elsewhere, but rather the economy appears to have adjusted along multiple margins.
                    </p>
                    <p style="margin: 0; font-size: 12px; color: #888; line-height: 1.4;">
                        <strong>Methodology:</strong><br>
                        The chart compares average component levels in two windows (2019–2021 vs 2022–2024) and plots the difference (post minus pre) for consumption, investment, and government spending. Net exports are computed as (X−M) in each window and then differenced; the total shift is the sum of all component deltas.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            with col_chart:
                st.plotly_chart(plot_fig2_decomposition(df, current_theme), config={'displayModeBar': False, 'responsive': True})

        st.markdown("---")

        st.title("3. CURRENT ACCOUNT")
        
        df_ca = get_current_account_data()
        
        if df_ca.empty:
            st.error("CONNECTION ERROR: UNABLE TO FETCH ECB DATA.")
        else:
            s3_data = get_s3_data()
            
            fig_goods = plot_fig2_goods_balance(s3_data, date_range, current_theme)
            if fig_goods:
                col_text, col_chart = st.columns([1, 3])
                with col_text:
                    figure_header("Figure 7")
                    st.markdown(f"""
                    <div class="geo-text" style="
                        background-color: {current_theme['paper']};
                        padding: 20px;
                        border-radius: 6px;
                        color: {current_theme['text']};
                        margin-top: 0px; 
                    ">
                        <p style="margin: 0 0 12px 0; font-size: 14px; line-height: 1.5;">
                            The deterioration around 2022 is concentrated in quarters immediately following the invasion, with the Russia component accounting for a large share of the initial swing, consistent with an adverse terms-of-trade shock in which import values rose relative to exports during the adjustment phase. From 2023 to 2024, the Russia-related component compresses noticeably, and the overall goods balance temporarily improves.
                        </p>
                        <p style="margin: 0; font-size: 12px; color: #888; line-height: 1.4;">
                            <strong>Methodology:</strong><br>
                            Quarterly goods-balance series are merged for total goods balance and the Russia component on a common date index. The ex-Russia balance is constructed as Total − Russia, and the figure plots Russia and ex-Russia as stacked bars (relative mode).
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_chart:
                    st.plotly_chart(fig_goods, config={'displayModeBar': False, 'responsive': True})
            else:
                st.info("Insufficient data for Goods Balance decomposition.")

            st.markdown("###")
            
            fig_bridge = plot_fig3_impact_bridge(s3_data, date_range, current_theme)
            if fig_bridge:
                col_text, col_chart = st.columns([1, 3])
                with col_text:
                    figure_header("Figure 8")
                    st.markdown(f"""
                    <div class="geo-text" style="
                        background-color: {current_theme['paper']};
                        padding: 20px;
                        border-radius: 6px;
                        color: {current_theme['text']};
                        margin-top: 0px; 
                    ">
                        <p style="margin: 0 0 12px 0; font-size: 14px; line-height: 1.5;">
                            Figure 8 shows how the current account closely tracks the goods balance, implying the invasion’s external impact operated primarily through trade rather than through offsets from other current account components. The sharp move into deficit by 2022 mirrors the goods-balance collapse, indicating that the external shock translated rapidly into an aggregate external deficit.
                        </p>
                        <p style="margin: 0; font-size: 12px; color: #888; line-height: 1.4;">
                            <strong>Methodology:</strong><br>
                            Monthly current-account values are aggregated to quarterly frequency by summing within each quarter, then merged with the quarterly total goods-balance series on date. The figure plots both time series on a shared visual scale (dual axes forced to the same range) and reports their sample correlation over the displayed window.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_chart:
                    st.plotly_chart(fig_bridge, config={'displayModeBar': False, 'responsive': True})
            else:
                st.info("Insufficient data for Impact Bridge analysis.")








if __name__ == "__main__":
    main()