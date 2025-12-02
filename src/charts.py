from config import PROCESSED_DIR
REPORTS_DIR = PROCESSED_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

def generate_kpi_charts(df: pd.DataFrame, reports_dir: Path = None):
    
    if reports_dir is None:
        reports_dir = REPORTS_DIR
    
    sns.set_style("whitegrid")
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    
    def convert_to_number(val):
        if pd.isna(val) or val == 'nan' or val == '' or val is None:
            return None
        val = str(val).upper().strip()
        val = val.replace('$', '').replace('USD', '').replace(',', '').replace('%', '')
        try:
            if 'B' in val:
                return float(val.replace('B', '')) * 1e9
            elif 'M' in val:
                return float(val.replace('M', '')) * 1e6
            else:
                return float(val)
        except:
            return None
    
    numeric_cols = ["revenue", "net_income", "gross_profit", "roa"]
    for col in numeric_cols:
        if col in df.columns:
            df[f"{col}_num"] = df[col].apply(convert_to_number)

    latest_year = df['year'].max()
    df_latest = df[df['year'] == latest_year].copy()
    
    df_latest = df_latest.dropna(subset=['revenue_num', 'net_income_num'])
    df_latest = df_latest[df_latest['revenue_num'] > 0]
    
    df_latest['profit_efficiency'] = (df_latest['net_income_num'] / df_latest['revenue_num']) * 100
    top_profit = df_latest.nlargest(10, 'profit_efficiency')
    
    if len(top_profit) > 0:
        fig, ax = plt.subplots(figsize=(12, 7))
        bars = ax.barh(range(len(top_profit)), top_profit['profit_efficiency'], color='#009E8C', height=0.7)
        ax.set_yticks(range(len(top_profit)))
        ax.set_yticklabels(top_profit['company_name'])
        ax.set_xlabel('Profit Margin (%)', fontweight='bold')
        ax.set_ylabel('Company', fontweight='bold')
        ax.set_title(f'Top 10 Companies by Profit Efficiency ({latest_year})', fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        
        for i, (bar, val) in enumerate(zip(bars, top_profit['profit_efficiency'])):
            ax.text(val + 1, i, f'{val:.1f}%', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(reports_dir / "kpi_profit_efficiency.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    df_sorted = df.sort_values(['company_name', 'year']).copy()
    df_sorted['revenue_growth'] = df_sorted.groupby('company_name')['revenue_num'].pct_change(fill_method=None) * 100
    
    latest_growth = df_sorted[df_sorted['year'] == latest_year].dropna(subset=['revenue_growth'])
    latest_growth = latest_growth[latest_growth['revenue_growth'].abs() < 200]
    top_growth = latest_growth.nlargest(10, 'revenue_growth')
    
    if len(top_growth) > 0:
        fig, ax = plt.subplots(figsize=(12, 7))
        colors = ['#0F5B8A' if x > 0 else '#E94B3C' for x in top_growth['revenue_growth']]
        bars = ax.barh(range(len(top_growth)), top_growth['revenue_growth'], color=colors, height=0.7)
        ax.set_yticks(range(len(top_growth)))
        ax.set_yticklabels(top_growth['company_name'])
        ax.set_xlabel('Revenue Growth (% YoY)', fontweight='bold')
        ax.set_ylabel('Company', fontweight='bold')
        ax.set_title(f'Top 10 Companies by Revenue Growth ({latest_year})', fontweight='bold', pad=20)
        ax.axvline(x=0, color='black', linewidth=0.8, linestyle='-')
        ax.grid(axis='x', alpha=0.3)
        
        for i, (bar, val) in enumerate(zip(bars, top_growth['revenue_growth'])):
            offset = 2 if val > 0 else -2
            ha = 'left' if val > 0 else 'right'
            ax.text(val + offset, i, f'{val:.1f}%', va='center', ha=ha, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(reports_dir / "kpi_revenue_growth.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    df_latest_roa = df_latest.dropna(subset=['roa_num'])
    top_roa = df_latest_roa.nlargest(10, 'roa_num')
    
    if len(top_roa) > 0:
        fig, ax = plt.subplots(figsize=(12, 7))
        bars = ax.barh(range(len(top_roa)), top_roa['roa_num'], color='#F9A03F', height=0.7)
        ax.set_yticks(range(len(top_roa)))
        ax.set_yticklabels(top_roa['company_name'])
        ax.set_xlabel('Return on Assets (%)', fontweight='bold')
        ax.set_ylabel('Company', fontweight='bold')
        ax.set_title(f'Top 10 Companies by ROA ({latest_year})', fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        
        for i, (bar, val) in enumerate(zip(bars, top_roa['roa_num'])):
            ax.text(val + 0.5, i, f'{val:.1f}%', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(reports_dir / "kpi_roa.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    df_latest_margin = df_latest.dropna(subset=['gross_profit_num'])
    df_latest_margin = df_latest_margin[df_latest_margin['revenue_num'] > 0]
    df_latest_margin['margin_strength'] = (df_latest_margin['gross_profit_num'] / df_latest_margin['revenue_num']) * 100
    top_margin = df_latest_margin.nlargest(10, 'margin_strength')
    
    if len(top_margin) > 0:
        fig, ax = plt.subplots(figsize=(12, 7))
        bars = ax.barh(range(len(top_margin)), top_margin['margin_strength'], color='#E94B3C', height=0.7)
        ax.set_yticks(range(len(top_margin)))
        ax.set_yticklabels(top_margin['company_name'])
        ax.set_xlabel('Gross Margin (%)', fontweight='bold')
        ax.set_ylabel('Company', fontweight='bold')
        ax.set_title(f'Top 10 Companies by Gross Margin ({latest_year})', fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        
        for i, (bar, val) in enumerate(zip(bars, top_margin['margin_strength'])):
            ax.text(val + 1, i, f'{val:.1f}%', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(reports_dir / "kpi_margin_strength.png", dpi=300, bbox_inches='tight')
        plt.close()

# USED AI to generate this function.