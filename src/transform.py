import json
import time
import yfinance as yf
import pandas as pd
from datetime import datetime
from config import RAW_DIR, PROCESSED_DIR

def load_selected_tickers():
    file_path = RAW_DIR / "selected_companies.json"
    return json.loads(file_path.read_text())

def get_company_info(ticker_str):
    try:
        ticker= yf.Ticker(ticker_str)
        info = ticker.info
        
        return {
            "country": info.get("country"),
            "industry": info.get("industry"),
            "currency": info.get("financialCurrency") or info.get("currency", "USD")
        }
    except:
        return {"country": None, "industry": None, "currency": "USD"} #if these tickers wont be found just use defauts

def calculate_kpis(ticker_str):
    try:
        ticker= yf.Ticker(ticker_str)
        
        inc_stmt= ticker.income_stmt
        balance = ticker.balance_sheet
        
        if inc_stmt.empty:
            return []
        
        years = inc_stmt.columns[:3] 
        rows = []
        
        for year_date in years:
            year = year_date.year #for getting last 3 years of data
            revenue = inc_stmt.loc["Total Revenue", year_date] if "Total Revenue" in inc_stmt.index else None
            if pd.isna(revenue) or revenue <= 0:
                continue
            # getting net income and gross profit 
            net_income = inc_stmt.loc["Net Income", year_date] if "Net Income" in inc_stmt.index else None
            gross_profit = inc_stmt.loc["Gross Profit", year_date] if "Gross Profit" in inc_stmt.index else None
            #calculating net margin and gross margin
            net_margin = (net_income / revenue * 100) if net_income and revenue else None
            gross_margin = (gross_profit / revenue * 100) if gross_profit and revenue else None
            #to calculate ROA
            roa = None
            if not balance.empty and "Net Income" in inc_stmt.index and "Total Assets" in balance.index:
                if year_date in balance.columns:
                    assets = balance.loc["Total Assets", year_date]
                    if assets and assets != 0:
                        roa = net_income / assets if net_income else None
            #eps can be fechted diretcly
            basic_eps = inc_stmt.loc["Basic EPS", year_date] if "Basic EPS" in inc_stmt.index else None
            
            rows.append({
                "year": year,
                "revenue": float(revenue) if revenue else None,
                "net_income": float(net_income) if net_income and not pd.isna(net_income) else None,
                "gross_profit": float(gross_profit) if gross_profit and not pd.isna(gross_profit) else None,
                "net_profit_margin": float(net_margin) if net_margin and not pd.isna(net_margin) else None,
                "gross_profit_margin": float(gross_margin) if gross_margin and not pd.isna(gross_margin) else None,
                "roa": float(roa) if roa and not pd.isna(roa) else None,
                "basic_eps": float(basic_eps) if basic_eps and not pd.isna(basic_eps) else None,
            })
        
        return rows
    
    except Exception as e:
        return []

def transform_all():
    companies = load_selected_tickers() #loading selected tickers or companies
    all_data = []
    
    for i, comp in enumerate(companies, 1):
        ticker = comp.get("ticker")
        name = comp.get("company_name")
        
        if not ticker:
            continue
        
        info = get_company_info(ticker)
        kpis = calculate_kpis(ticker)
        
        #combining all the kpis and company data into a single row
        for kpi_row in kpis:
            row = {
                "ticker": ticker,
                "company_name": name,
                "country": info["country"],
                "industry": info["industry"],
                "year": kpi_row["year"],
                "revenue": kpi_row["revenue"],
                "revenue_unit": info["currency"],
                "net_income": kpi_row["net_income"],
                "gross_profit": kpi_row["gross_profit"],
                "net_profit_margin": kpi_row["net_profit_margin"],
                "gross_profit_margin": kpi_row["gross_profit_margin"],
                "roa": kpi_row["roa"],
                "basic_eps": kpi_row["basic_eps"],
            }
            all_data.append(row)
        time.sleep(0.3)  
    return all_data

def save_processed(data):
    df= pd.DataFrame(data) #convert to a dataframe
    csv_path= PROCESSED_DIR / "financial_data.csv"
    json_path = PROCESSED_DIR / "financial_data.json"
    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", indent=2)
    
    return df
