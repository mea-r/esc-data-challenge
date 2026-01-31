import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import numpy as np
import sys
from theme import apply_plot_theme

def get_data(file):
    df = pd.read_csv(file)
    df.rename(columns = {df.columns[0]: "Date", df.columns[2]: "Value", 
                         df.columns[1]: "Time Period"}, inplace = True)
    df = df[["Date", "Time Period", "Value"]]
    df["Date"] = pd.to_datetime(df["Date"])
    df = df[df["Date"] >= "2019-January"]
    return df

def create_figure(title):
    fig = go.Figure().update_layout(
        template ="plotly_white", 
        title = f"<b>{title}</b>", 
        title_x = 0.5, 
        title_y = 0.925, 
        title_font_weight = 600,
        font=dict(color="#2A3F5F", family="Georgia"),
        title_font=dict(color="#2A3F5F", family="Georgia", size=24)
    )
    fig.update_layout(width = 750, height = 450)
    fig.update_xaxes(
        range=[pd.Timestamp("2019-January"), pd.Timestamp("2026-January")],
        tickfont=dict(color="#2A3F5F"),
        title_font=dict(color="#2A3F5F")
    )
    return fig

def plot(df, fig, color, name):
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Value"], 
                             line = dict(width = 3, color = color),
                             name = name))

def log_transform(df):
    return df.apply(np.log)

def sqrt_tranformation(df):
    ser = df["Value"].apply(np.sqrt)
    df["Value"] = ser
    return df

def z_score_conversion(df):
    for col in df.columns[2:]:
        df[col] = (df[col] - df[col].mean())/ df[col].std()
    return df

def rebase(df, base_date):
    baser = df.loc[df["Time Period"] == "2022Jan"]["Value"]
    ser = df["Value"].apply(lambda x: (x/baser)*100)
    df["Value"] = ser
    return df

def get_unit_value(Value_df, Volume_df):
    ser_div = Value_df["Value"].div(Volume_df["Value"])
    ser_div = ser_div.apply(lambda x: x*100)
    df = pd.DataFrame()
    df["Date"] = Value_df["Date"]
    df["Value"] = ser_div
    return df

def legend_setting(fig):
    fig.update_layout(legend = dict(orientation = "h", x=0.5, xanchor="center"))


def find_min_max(lst:list, fig):
    maxy, miny, = lst[0]["Value"].min(), lst[0]["Value"].max()
    for df in lst:
        if df["Value"].min() < miny:
            miny = df["Value"].min()
        if df["Value"].max() > maxy:
            maxy = df["Value"].max()
    
    fig.update_yaxes(range = [miny, maxy])




def plot_price_stability(vol_file="data/Gas_Vol.csv", val_file="data/Gas_Val.csv", theme=None, overview_mode=False):

    try:
        df_Val = get_data(val_file)
        df_Vol = get_data(vol_file)
    except FileNotFoundError:
        return None

    title = "Petroleum Imports: EA with Extra EA - Value vs Volume"
    if overview_mode:
        title = "" 
        
    fig = create_figure(title)

    df_Val = rebase(df_Val, "2022-January")
    df_Vol = rebase(df_Vol, "2022-January")
    df_unit = get_unit_value(df_Val, df_Vol)
    
    plot(df_Val, fig, "#2E6BFF", "Value")
    plot(df_Vol, fig, "#4CC9F0", "Volume")
    plot(df_unit, fig, "#FFCC00", "Unit price")

    legend_setting(fig)
    fig.add_vline(x=pd.Timestamp("2022-February"), line_width = 3, line_dash = "dash", line_color = "#2A3F5F")
    
    fig.update_layout(margin=dict(t=70, b=20, l=80, r=60))
    fig.update_layout(
        font=dict(family="Georgia", size=16, color="#2A3F5F"),
        legend=dict(
            font=dict(family="Georgia", size=16, color="#2A3F5F"),
        )
    )
    fig.for_each_trace(lambda t: t.update(name = f"<b>{t.name}</b>"))

    if overview_mode:
        fig.update_xaxes(
            tickfont=dict(color="#2A3F5F", family="Georgia", size=10),
            title_font=dict(color="#2A3F5F", family="Georgia", size=10)
        )
        fig.update_yaxes(
            title="Index (Jan-2022 = 100)",
            tickfont=dict(color="#2A3F5F", family="Georgia", size=10),
            title_font=dict(color="#2A3F5F", family="Georgia", size=10)
        )
    else:
        fig.update_xaxes(
            tickfont=dict(color="#2A3F5F", family="Georgia", size=16),
            title_font=dict(color="#2A3F5F", family="Georgia", size=18),
            tickprefix="<b>", ticksuffix="</b>"
        )
        fig.update_yaxes(
            title="<b>Index (Jan-2022 = 100)</b>",
            tickfont=dict(color="#2A3F5F", family="Georgia", size=16),
            title_font=dict(color="#2A3F5F", family="Georgia", size=18),
            tickprefix="<b>", ticksuffix="</b>"
        )
    
    fig.update_layout(margin = dict(autoexpand = False))
    fig.update_layout(margin_b = 70)
    

    fig = apply_plot_theme(fig)

    if not overview_mode:
        fig.add_annotation(xref = "x1", yref = "y1", x="2022-08-01", y = 168, 
                                            text = "A", 
                                            showarrow=True, 
                                            arrowhead=1,
                                            arrowcolor="#2A3F5F",
                                            arrowwidth=2.5,
                                            font = dict(color = "#2A3F5F", size = 16, weight = 1000),
                                            ay = -10, ax = 100)
        
        fig.add_annotation(xref = "x1", yref = "y1", x="2023-02-01", y = 85, 
                                            text = "B", 
                                            showarrow=True, 
                                            arrowhead=1,
                                            arrowcolor="#2A3F5F",
                                            arrowwidth=2.5,
                                            font = dict(color = "#2A3F5F", size = 16, weight = 1000),
                                            ay = 100, ax = -40)

    return fig

if __name__ == "__main__":

    fig = plot_price_stability()
    if fig:
        fig.write_image("Euro_Area_Value_V_Volume2_light_2.png", width = 750, height = 450, scale = 6)