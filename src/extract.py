import requests
import json
import time 
from config import RAW_DIR, SEC_URL, HEADERS

def fetch_sec_tickers(force=False):
    out_file = RAW_DIR / "company_tickers.json"
    if out_file.exists() and not force:
        try:
            return json.loads(out_file.read_text())
        except Exception:
            pass
    r = requests.get(SEC_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    items = []
    for k, v in data.items():
        items.append({
            "ticker": v.get("ticker").upper(),
            "company_name": v.get("title")
        })
    out_file.write_text(json.dumps(items))
    time.sleep(0.2)
    return items

def pick_tickers(all_items, limit=150):
    seen = set()
    sel = [] #selected companies store
    for it in all_items:
        t = it["ticker"]
        if t in seen:
            continue #dont add same company again
        seen.add(t)
        sel.append(it)
        if len(sel) >= limit:
            break
    return sel
