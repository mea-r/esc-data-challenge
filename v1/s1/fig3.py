import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os
from theme import apply_plot_theme

def get_data():
    base_dir = "data/s1fig3"
    
    files = {
        "energy_poland": os.path.join(base_dir, "Data/HICP - Energy, Poland, Monthly.csv"),
        "neer_ea": os.path.join(base_dir, "Data/Nominal effective exchange rate, Euro area_Broad basket.csv"),
        "neer_poland": os.path.join(base_dir, "Data/Nominal effective exchange rate, Poland_Broad basket.csv")
    }

    def load_safe(path):
        if os.path.exists(path):
            return pd.read_csv(path)
        return pd.DataFrame()

    df_energy_poland = load_safe(files["energy_poland"])
    df_ex_ea = load_safe(files["neer_ea"])
    df_ex_poland = load_safe(files["neer_poland"])
    
    def filter_dates(df):
        if not df.empty and "DATE" in df.columns:
            df["DATE"] = pd.to_datetime(df["DATE"])
            df = df[df["DATE"] >= "2019-January"]
        return df

    return filter_dates(df_energy_poland), filter_dates(df_ex_ea), filter_dates(df_ex_poland)

def create_figure(title):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(template ="plotly_white", title = title, title_x = 0.5, title_y = 0.925, title_font_weight = 600)
    fig.update_layout(width = 800, height = 450)
    return fig

def rebase(df, base_date):
    if df.empty: return df
    try:
        target = pd.Timestamp("2022-01-31")
        mask = (df["DATE"].dt.year == 2022) & (df["DATE"].dt.month == 1)
        if mask.any():
            baser = df.loc[mask, "OBS_VALUE:Value"].iloc[0]
            if baser != 0:
                ser = df["OBS_VALUE:Value"].apply(lambda x: (x/baser)*100)
                df["OBS_VALUE:Value"] = ser
    except Exception as e:
        print(f"Rebase error: {e}")
    return df

def plot(df, fig, color, name, col, sec_y, x = "DATE"):
    if df.empty: return
    if col not in df.columns:
        print(f"Column '{col}' not found in dataframe for {name}")
        return

    fig.add_trace(go.Scatter(x=df[x], y=df[col], 
                             line = dict(width = 3, color = color),
                             name = name),
                             secondary_y = sec_y)


def touch_up(fig):
    fig.update_layout(margin=dict(t=70, b=100, l=80, r=25))
    fig.update_layout(font_family = "Georgia", font_weight = 600, font_size = 18)
    fig.add_vline(x=pd.Timestamp("2022-February"), line_width = 3, line_dash = "dash",
                                 line_color = "#2A3F5F")
    fig.update_yaxes(title = "NEER Index (Jan-2022 = 100)", secondary_y = False)
    fig.update_yaxes(title = "HICP Energy Inflation (YoY. %)", secondary_y = True)
    fig.update_layout(margin = dict(autoexpand = False))

    fig.update_layout(paper_bgcolor = "#F3F4F6")
    fig.update_layout(plot_bgcolor = "#F3F4F6")
    fig.update_layout(legend = dict(orientation = "h", x=0.5, y=-0.18, xanchor="center"))
    fig.update_yaxes(tickprefix = " ", secondary_y=True)
    fig.update_yaxes(ticksuffix = " ", secondary_y=False)

def plot_exchange_rate_inflation():
    try:
        df_energy_poland, df_ex_ea, df_ex_poland = get_data()
        
        if df_energy_poland.empty and df_ex_ea.empty and df_ex_poland.empty:
            return None

        fig = create_figure("Exchange Rate and Energy Inflation")
        
        df_ex_ea = rebase(df_ex_ea, "2022-January")
        df_ex_poland = rebase(df_ex_poland, "2022-January")
        
        plot(df_energy_poland, fig, "#FFCC00", "Poland Energy HICP", "HICP - Energy (ICP.M.PL.N.NRGY00.4.ANR)", True)
        plot(df_ex_ea, fig, "#2E6BFF", "Poland NEER", "OBS_VALUE:Value", False)
        plot(df_ex_poland, fig, "#4CC9F0", "EA NEER", "OBS_VALUE:Value", False)
        
        touch_up(fig)
        
        fig = apply_plot_theme(fig)
        
        return fig
    except Exception as e:
        print(f"Error in fig4: {e}")
        return None

if __name__ == "__main__":
    fig = plot_exchange_rate_inflation()
    if fig:
        fig.show(renderer = "browser")