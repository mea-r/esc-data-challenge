import plotly.graph_objects as go
import pandas as pd
import os

def get_data():
    base_dir = "data/s1fig2_5"
    weights_dir = f"{base_dir}/weights"
    values_dir = f"{base_dir}/data" 
    
    headline_file = f"{base_dir}/HICP - Overall index, Poland, Monthly.csv"

    if not os.path.exists(headline_file):
        print(f"File not found: {headline_file}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    df_headline = pd.read_csv(headline_file)
    df_headline["DATE"] = pd.to_datetime(df_headline["DATE"])
    df_headline = df_headline[df_headline["DATE"] >= "2019-January"]

    def recursive_df_merge(lst):
        if len(lst) == 1:
            return lst[0]
        else:
            lst[1] = lst[0].merge(right=lst[1], how = "left", on = "DATE")
            lst.pop(0)
            return recursive_df_merge(lst)

    def filter_dates(lst):
        updated_df_lst = []
        for df in lst:
            df["DATE"] = pd.to_datetime(df["DATE"])
            df = df[df["DATE"] >= "2019-January"]
            updated_df_lst.append(df)
        return updated_df_lst
    
    def drop_time_period(lst):
        updated_df_lst = []
        for df in lst:
            df = df.drop(["TIME PERIOD"], axis = 1)
            updated_df_lst.append(df)
        return updated_df_lst
    

    if os.path.exists(values_dir):
        values_files = sorted([f for f in os.listdir(values_dir) if f.endswith(".csv")])
        df_values_lst = [pd.read_csv(os.path.join(values_dir, file_name)) for file_name in values_files]
    else:

        df_values_lst = []


    if os.path.exists(weights_dir):
        weights_files = sorted([f for f in os.listdir(weights_dir) if f.endswith(".csv")])
        df_weights_lst = [pd.read_csv(os.path.join(weights_dir, file_name)) for file_name in weights_files]
    else:
        df_weights_lst = []

    if not df_values_lst or not df_weights_lst:
        return pd.DataFrame(), pd.DataFrame(), df_headline

    return recursive_df_merge(filter_dates(drop_time_period(df_values_lst))), recursive_df_merge(drop_time_period(filter_dates(df_weights_lst))), df_headline 


def adjust_dataframes(df_val, df_weight):

    df_val.drop(["HICP - Overall index (ICP.M.PL.N.000000.4.ANR)"], axis = 1, inplace = True)

    def get_corresponding_col_data(col_id):
        for col in df_weight.columns:
            if col.startswith(col_identifier):
                return col

    for column in df_val.columns[1:]:
        row_counter = 0
        values_v = []

        for val in df_val[column].values:
            year = df_val["DATE"].iloc[row_counter].year

            col_identifier = column[:10]
            corresponding_col = get_corresponding_col_data(col_identifier)

            
            multiplier = df_weight[corresponding_col].loc[df_weight["DATE"].dt.year == year]
            values_v.append(float((multiplier.iloc[0]/1000)*val))
            row_counter +=1

        df_val[column] = values_v

    return df_val


def create_figure(title):
    fig = go.Figure().update_layout(template ="plotly_white", title = title, title_x = 0.5, title_y = 0.925, title_font_weight = 600)
    fig.update_layout(width = 1000, height = 450)
    return fig

def plot_bar(df, fig, names: list, colors):
    counter = 0
    for col in df.columns[1:]:
        fig.add_trace(go.Bar(name = names[counter], x=df["DATE"], 
                             y = df[col], marker_color = colors[counter]))
        counter +=1

    fig.update_layout(barmode = "relative")

def plot_line(df, fig):
    fig.add_trace(go.Scatter(name = "Headline", x=df["DATE"], y=df[df.columns[2]],
                             line = dict(width = 4, dash = "dash")))
    

def touch_up(fig):

    fig.add_shape(
        type="line",
        x0="2022-02-24", x1="2022-02-24",
        y0=0, y1=18, 
        xref="x", yref="y",
        line=dict(width=4.2, dash="dash", color = "#2A3F5F"))
    
    fig.update_layout(margin=dict(t=70, b=100, l=80, r=60))
    fig.update_layout(font_family = "Georgia", font_weight = 600, font_size = 18)
    fig.update_layout(legend = dict(orientation = "h", x=0.5, xanchor="center"))
    fig.update_layout(yaxis_title = "pp (YoY)")
    fig.update_layout(paper_bgcolor = "#F3F4F6")
    fig.update_layout(plot_bgcolor = "#F3F4F6")



def plot_hicp_contribution():
    try:
        df_val, df_vol, df_headline = get_data()
        df_weighted = adjust_dataframes(df_val, df_vol)
        
        cols = df_weighted.columns.tolist()
        date_col = cols[0]
        core_col = next(c for c in cols if "All-items" in c)
        energy_col = next(c for c in cols if "Energy" in c)
        food_col = next(c for c in cols if "Food" in c)
        
        df_weighted = df_weighted[[date_col, core_col, energy_col, food_col]]
        
        fig = create_figure("Headline HICP YoY Contribution (Poland)")
        plot_bar(df_weighted, fig, ["Core", "Food", "Energy"], ["#2E6BFF", "#4CC9F0", "#FFCC00"])
        touch_up(fig)
        from theme import apply_plot_theme
        fig = apply_plot_theme(fig)
        
        return fig
    except Exception as e:
        print(f"Error generating HICP chart: {e}")
        return None

if __name__ == "__main__":
    fig = plot_hicp_contribution()
    if fig:
        fig.show(renderer = "browser")