from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

SEC_URL = "https://www.sec.gov/files/company_tickers.json"
HEADERS = {"User-Agent": "kotavenkateshgnanashri@gmail.com"}