import pandas as pd
import re
from config import PROCESSED_DIR

def clean_numeric(value):
    if pd.isna(value):
        return None
    v = str(value)
    v = v.replace(",", "")
    v = re.sub(r"[^0-9eE\.\-]", "", v)
    try:
        return float(v)
    except:
        return None

def format_large_num(value): #to format the revenue numbers 
    if pd.isna(value):
        return None
    value = float(value)
    if value >= 1e12:
        return f"{value/1e12:.2f} T"
    elif value >= 1e9:
        return f"{value/1e9:.2f} B"
    elif value >= 1e6:
        return f"{value/1e6:.2f} M"
    else:
        return f"{value:,.0f}"

def clean_data(df):
    df = df.dropna(subset=["company_name"]).copy() #drop rows if company is missing 
    df["revenue"] = df["revenue"].apply(clean_numeric)
    
    df = df.sort_values(["ticker", "year"])

    # linear interpolate kpis in order to get smooth trends, typically adding middle value
    interpolate_cols = ['net_income', 'gross_profit_margin', 'roa']
    for col in interpolate_cols:
        if col in df.columns:
            df[col] = df.groupby("ticker")[col].transform(lambda x: x.interpolate(method='linear')) 

    #in case of eps, tricky to just add a middle value, so I used the last known value
    ffill_cols = ['basic_eps']  
    for col in ffill_cols:
        if col in df.columns:
            df[col] = df.groupby("ticker")[col].ffill()
    
    #first rounding and then formatting the values
    if 'net_income' in df.columns:
        df['net_income'] = df['net_income'].apply(format_large_num)
    if 'gross_profit' in df.columns:
        df['gross_profit'] = df['gross_profit'].apply(format_large_num)
    
    round_cols = ['basic_eps']
    for col in round_cols:
        if col in df.columns:
            df[col] = df[col].round(4)

    percent_cols = ['net_profit_margin', 'gross_profit_margin']
    for col in percent_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else None)
        
    if 'roa' in df.columns:
        df['roa'] = df['roa'].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else None)

    df["revenue"] = df["revenue"].apply(format_large_num)
    
    print(f"Total number of companies: {df['ticker'].nunique()}")
    return df
#load data
def save_cleaned_data(df):
    csv_path = PROCESSED_DIR / "financial_data_cleaned.csv"
    json_path = PROCESSED_DIR / "financial_data_cleaned.json"
    
    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", indent=2)
    return df
