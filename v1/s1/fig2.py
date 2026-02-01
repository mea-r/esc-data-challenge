import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os
from theme import apply_plot_theme

def get_data():
    base_dir = "data/s1fig2"

    def recursive_df_merge(lst):
        if not lst: return pd.DataFrame()
        if len(lst) == 1:
            return lst[0]
        else:
            lst[1] = lst[0].merge(right=lst[1], how = "left", on = "DATE")
            lst.pop(0)
            return recursive_df_merge(lst)

    def filter_dates(lst):
        updated_df_lst = []
        for df in lst:
            if "DATE" in df.columns:
                df["DATE"] = pd.to_datetime(df["DATE"])
                df = df[df["DATE"] >= "2019-January"]
                updated_df_lst.append(df)
        return updated_df_lst
    
    def drop_time_period(lst):
        updated_df_lst = []
        for df in lst:
            if "TIME PERIOD" in df.columns:
                df = df.drop(["TIME PERIOD"], axis = 1)
            updated_df_lst.append(df)
        return updated_df_lst
    
    def load_from_dir(subdir):
        target_dir = os.path.join(base_dir, subdir)
        if not os.path.exists(target_dir):
            return []
        files = sorted([f for f in os.listdir(target_dir) if f.endswith(".csv")])
        return [pd.read_csv(os.path.join(target_dir, f)) for f in files]

    df_poland_val = load_from_dir("poland_data")
    df_poland_weights = load_from_dir("poland_weights")
    df_ea_val = load_from_dir("ea_data")
    df_ea_weights = load_from_dir("ea_weights")

    return (
        recursive_df_merge(filter_dates(drop_time_period(df_poland_val))), 
        recursive_df_merge(filter_dates(drop_time_period(df_poland_weights))), 
        recursive_df_merge(filter_dates(drop_time_period(df_ea_val))), 
        recursive_df_merge(filter_dates(drop_time_period(df_ea_weights)))
    )

def adjust_dataframes(df_val, df_weight):
    if df_val.empty or df_weight.empty:
        return df_val

    def get_corresponding_col_data(col_identifier):
        for col in df_weight.columns:
            if col.startswith(col_identifier):
                return col
        return None

    for column in df_val.columns[1:]: 
        row_counter = 0
        values_v = []
        

        
        limit = min(len(df_val), len(df_weight))
        
        for val in df_val[column].values:
            if row_counter >= len(df_val): break
            
            date_val = df_val["DATE"].iloc[row_counter]
            year = date_val.year

            col_identifier = column[:10]
            corresponding_col = get_corresponding_col_data(col_identifier)
            
            if corresponding_col:

                weight_subset = df_weight[corresponding_col].loc[df_weight["DATE"].dt.year == year]
                if not weight_subset.empty:
                    multiplier = weight_subset.iloc[0]
                    values_v.append(float((multiplier/1000)*val))
                else:
                    values_v.append(0.0)
            else:
                 values_v.append(0.0)
                 
            row_counter +=1

        df_val[column] = values_v

    return df_val

def create_figure(title):
    fig = make_subplots(rows = 2, cols = 1, subplot_titles = ["Poland", "Euro Area"],
                        shared_yaxes = True,
                        vertical_spacing = 0.09)
    fig.update_layout(template ="plotly_white", title = title, title_x = 0.5, title_y = 0.96, title_font_weight = 600)
    fig.update_layout(width = 900, height = 650)

    fig.update_yaxes(range = [-0.75748, 17.338017], row = 1, col = 1)
    fig.update_yaxes(range = [-1.176565, 17.338017], row = 2, col = 1)
    return fig

def plot_bar(df, fig, names: list, colors, loc, show_leg, leg_name):
    if df.empty: return
    counter = 0
    cols = df.columns[1:]
    for i, col in enumerate(cols):
        if counter < len(names):
            name_label = names[counter]
            color_val = colors[counter]
        else:
            name_label = col
            color_val = "#CCCCCC"

        fig.add_trace(go.Bar(name = name_label, x=df["DATE"], 
                             y = df[col], marker_color = color_val,
                             legendgroup="group" + str(counter), showlegend=show_leg, legend = leg_name),
                             row = loc, col = 1)
        counter +=1

    fig.update_layout(barmode = "relative")

def touch_up(fig):
    for i in range(1, 3):
        fig.add_shape(
            type="line",
            x0="2022-02-24", x1="2022-02-24",
            y0=0, y1=18, 
            xref="x", yref=f"y{i if i==1 else ''}", 
            line=dict(width=4.2, dash="dash", color = "#2A3F5F"), 
            row = i, col = 1
        )
    
    fig.update_layout(margin=dict(t=140, b=100, l=80, r=60))

    fig.update_layout(font_family = "Georgia", font_weight = 600, font_size = 18)
    fig.update_yaxes(title_text = "pp (YoY)", row = 1, col = 1)
    fig.update_yaxes(title_text = "pp (YoY)", row = 2, col = 1)
    fig.update_layout(paper_bgcolor = "#F3F4F6")
    fig.update_layout(plot_bgcolor = "#F3F4F6")
    fig.update_layout(legend1 = dict(orientation = "h", x=0.5, y=-0.12, xanchor="center"))


    if len(fig.layout.annotations) >= 2:
        try:
            fig.layout.annotations[0].update(x=0.525, font=dict(size=20), y=1.02)
            fig.layout.annotations[1].update(x=0.54, font=dict(size=20), y=0.4)
        except:
            pass

def plot_inflation_comparison():
    try:
        df_poland_val, df_poland_weights, df_ea_val, df_ea_weights = get_data()
        

        if df_poland_val.empty and df_ea_val.empty:
            return None

        df_poland_weighted = adjust_dataframes(df_poland_val, df_poland_weights)
        df_ea_weighted = adjust_dataframes(df_ea_val, df_ea_weights)
        
        fig = create_figure("Headline HICP YoY Contribution")
        

        comps = ["Core", "Food", "Energy"]
        cols = ["#2E6BFF", "#4CC9F0", "#FFCC00"]
        
        p_cols = df_poland_weighted.columns.tolist()
        p_date = p_cols[0]
        p_core = next(c for c in p_cols if "All-items" in c)
        p_energy = next(c for c in p_cols if "Energy" in c)
        p_food = next(c for c in p_cols if "Food" in c)
        
        df_poland_weighted = df_poland_weighted[[p_date, p_core, p_energy, p_food]]

        e_cols = df_ea_weighted.columns.tolist()
        e_date = e_cols[0]
        e_core = next(c for c in e_cols if "All-items" in c)
        e_energy = next(c for c in e_cols if "Energy" in c)
        e_food = next(c for c in e_cols if "Food" in c)
        
        df_ea_weighted = df_ea_weighted[[e_date, e_core, e_energy, e_food]]

        plot_bar(df_poland_weighted, fig, comps, cols, 1, False, "legend1")
        plot_bar(df_ea_weighted, fig, comps, cols, 2, True, "legend1")
        
        touch_up(fig)
        

        fig = apply_plot_theme(fig)
        
        return fig
    except Exception as e:
        print(f"Error in fig3: {e}")
        return None

if __name__ == "__main__":
    fig = plot_inflation_comparison()
    if fig:
        fig.show(renderer = "browser")