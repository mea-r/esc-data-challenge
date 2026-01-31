import pandas as pd
import requests
import io
import os
import time
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def fetch_ecb_data(resource, flow_ref, key, params=None):

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    file_path = os.path.join(DATA_DIR, f"{key}.csv")


    if os.path.exists(file_path):

        try:
            df = pd.read_csv(file_path)

            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
            return df
        except Exception as e:
            print(f"Error loading cache for {key}: {e}")

    base_url = f"https://data-api.ecb.europa.eu/service/data/{flow_ref}/{key}"
    if params is None: params = {'format': 'csvdata'}
    
    try:
        print(f"Fetching {key} from API...")
        time.sleep(0.2)
        response = requests.get(base_url, params=params, timeout=60)
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.text))
        df.columns = [c.upper() for c in df.columns]
        col_map = {'TIME_PERIOD': 'Date', 'PERIOD': 'Date', 'OBS_VALUE': 'Value', 'VALUE': 'Value'}
        df = df.rename(columns=col_map)
        
        if 'Date' not in df.columns or 'Value' not in df.columns: 
            print(f"Missing columns for {key}")
            return pd.DataFrame()

        def parse_date(date_str):
            date_str = str(date_str).strip()

            if 'Q1' in date_str: return pd.Timestamp(f"{date_str[:4]}-03-31")
            if 'Q2' in date_str: return pd.Timestamp(f"{date_str[:4]}-06-30")
            if 'Q3' in date_str: return pd.Timestamp(f"{date_str[:4]}-09-30")
            if 'Q4' in date_str: return pd.Timestamp(f"{date_str[:4]}-12-31")
            
            try:
                return pd.to_datetime(date_str) + pd.offsets.MonthEnd(0)
            except:
                pass
            
            return pd.NaT

        df['Date'] = df['Date'].apply(parse_date)
        df = df.sort_values('Date')
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        

        final_df = df[['Date', 'Value']]
        final_df.to_csv(file_path, index=False)
        
        return final_df
    except Exception as e:
        print(f"Error fetching {key}: {e}")
        return pd.DataFrame()


def get_growth_data():

    
    df_ea = fetch_ecb_data("data", "MNA", "Q.Y.I9.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.N")
    df_pl = fetch_ecb_data("data", "MNA", "Q.Y.PL.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.N")
    df_cons = fetch_ecb_data("data", "MNA", "Q.Y.PL.W0.S1M.S1.D.P31._Z._Z._T.EUR.LR.N")
    df_inv = fetch_ecb_data("data", "MNA", "Q.Y.PL.W0.S1.S1.D.P51G.N11G._T._Z.EUR.LR.N")
    df_gov = fetch_ecb_data("data", "MNA", "Q.Y.PL.W0.S13.S1.D.P3._Z._Z._T.EUR.LR.N")
    df_exp = fetch_ecb_data("data", "MNA", "Q.Y.PL.W1.S1.S1.D.P6._Z._Z._Z.EUR.LR.N")
    df_imp = fetch_ecb_data("data", "MNA", "Q.Y.PL.W1.S1.S1.C.P7._Z._Z._Z.EUR.LR.N")

    if df_ea.empty or df_pl.empty: return pd.DataFrame()

    df = df_ea.rename(columns={'Value': 'EA_GDP'})

    def merge_comp(base, comp, name):
        if comp.empty: return base
        return pd.merge(base, comp.rename(columns={'Value': name}), on='Date', how='left')

    df = merge_comp(df, df_pl, 'PL_GDP')
    df = merge_comp(df, df_cons, 'Consumption')
    df = merge_comp(df, df_inv, 'Investment')
    df = merge_comp(df, df_gov, 'Gov_Spending')
    df = merge_comp(df, df_exp, 'Exports')
    df = merge_comp(df, df_imp, 'Imports')
    return df[df['Date'] >= '1996-01-01'].reset_index(drop=True)


def get_current_account_data():
    key_pl = "Q.Y.PL.W1.S1.S1.B.B11._Z._Z._Z.EUR.V.N"
    key_ea = "Q.Y.I9.W1.S1.S1.B.B11._Z._Z._Z.EUR.V.N"

    df_pl = fetch_ecb_data("data", "MNA", key_pl)
    df_ea = fetch_ecb_data("data", "MNA", key_ea)

    if df_pl.empty or df_ea.empty:
        return pd.DataFrame()

    df = pd.merge(df_pl.rename(columns={'Value': 'PL_CA'}), 
                  df_ea.rename(columns={'Value': 'EA_CA'}), 
                  on='Date', how='inner')
    
    return df[df['Date'] >= '2015-01-01'].sort_values('Date').reset_index(drop=True)





def get_s3_data():

    datasets = {
        "PL_CA_Monthly": "M.N.PL.W1.S1.S1.T.B.CA._Z._Z._Z.EUR._T._X.N.ALL",
        "EA_CA_Monthly": "M.N.I9.W1.S1.S1.T.B.CA._Z._Z._Z.EUR._T._X.N.ALL",
        "PL_Goods_Total": "Q.N.PL.W1.S1.S1.T.B.G._Z._Z._Z.EUR._T._X.N.ALL",
        "PL_Goods_Russia": "Q.N.PL.RU.S1.S1.T.B.G._Z._Z._Z.EUR._T._X.N.ALL"
    }
    
    results = {}
    for name, key in datasets.items():
        df = fetch_ecb_data("data", "BPS", key)
        if not df.empty:
            results[name] = df
        else:
            print(f"Warning: Failed to fetch {name} ({key})")
            results[name] = pd.DataFrame()
    

            
    return results
