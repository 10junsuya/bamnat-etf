"""과거 미국 종가 출처 후보 접속 확인(한 번씩). 결과 → data/probe.json"""
import json, urllib.request
from pathlib import Path
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
      "Accept": "application/json,text/plain,*/*", "Accept-Language": "en-US,en;q=0.9"}
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
        return r.read().decode("utf-8", "replace")
out = {}
for k, u in {"yahoo_q1": "https://query1.finance.yahoo.com/v8/finance/chart/SPY?range=1mo&interval=1d",
             "yahoo_q2": "https://query2.finance.yahoo.com/v8/finance/chart/BRK-B?range=1mo&interval=1d",
             "nasdaq": "https://api.nasdaq.com/api/quote/SPY/historical?assetclass=etf&fromdate=2026-10-20&limit=30",
             "stooq": "https://stooq.com/q/d/l/?s=spy.us&i=d"}.items():
    try:
        b = get(u); out[k] = {"len": len(b), "head": b[:700]}
    except Exception as e:  # noqa: BLE001
        out[k] = {"err": f"{type(e).__name__}: {str(e)[:160]}"}
Path("data/probe.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
