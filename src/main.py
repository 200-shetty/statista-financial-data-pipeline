import sys
import traceback
import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from extract import fetch_sec_tickers, pick_tickers
from transform import transform_all, save_processed
from clean_and_load import clean_data, save_cleaned_data
from config import RAW_DIR, PROCESSED_DIR
from charts import generate_kpi_charts


def main():
    try:
        sec_data = fetch_sec_tickers()
        selected = pick_tickers(sec_data, limit=150)
        selected_file = RAW_DIR / "selected_companies.json"
        selected_file.write_text(json.dumps(selected, indent=2))
        raw_data = transform_all()
        df_processed = save_processed(raw_data)
        df_cleaned = clean_data(df_processed)
        save_cleaned_data(df_cleaned)
        generate_kpi_charts(df_cleaned)
    except Exception:
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
