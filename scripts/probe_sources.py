"""구성종목 출처 후보 접속 확인(한 번씩). 결과 → data/probe.json"""
import json, re, urllib.request
from pathlib import Path
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"}
URLS = {
 "smh": "https://www.vaneck.com/etf/equity/smh/holdings",
 "schd_wallst": "https://www.schwab.wallst.com/Prospect/Research/etfs/portfolio.asp?symbol=SCHD",
 "schd_sam": "https://www.schwabassetmanagement.com/allholdings/SCHD",
 "funetf_465580": "https://www.funetf.co.kr/product/etf/view/KR7465580009",
 "funetf_381170": "https://www.funetf.co.kr/product/etf/view/KR7381170003",
 "mirae_381170": "https://investments.miraeasset.com/tigeretf/ko/product/search/detail/index.do?ksdFund=KR7381170003",
 "tigeretf_381170": "https://www.tigeretf.com/ko/product/search/detail/index.do?ksdFund=KR7381170003",
 "ace_search": "https://www.aceetf.co.kr/fund/search?keyword=465580",
 "soletf_list": "https://www.soletf.com/ko/fund",
 "indxx_tech10": "https://www.indxx.com/indices/thematic/indxx-us-tech-top-10-index",
}
out = {}
for k, u in URLS.items():
    try:
        req = urllib.request.Request(u, headers={**UA, "Referer": u.split("/", 3)[0] + "//" + u.split("/")[2] + "/"})
        with urllib.request.urlopen(req, timeout=40) as r:
            b = r.read().decode("utf-8", "replace")
            st = r.status
    except Exception as e:  # noqa: BLE001
        out[k] = {"err": f"{type(e).__name__}: {str(e)[:120]}"}; continue
    pct = re.findall(r">\s*(\d{1,2}\.\d{1,2})\s*%?\s*<", b)
    tick = sorted(set(re.findall(r">\s*(NVDA|AAPL|MSFT|AVGO|LMT|TXN|KO|PEP|CVX|ABBV|MRK|GOOGL|META|AMZN|TSLA)\s*<", b)))
    links = sorted(set(re.findall(r'href="([^"]*(?:fund/etf/\d+|fund/[A-Z0-9]{8,}|Holding|holding|xls|pdf)[^"]*)"', b)))[:25]
    out[k] = {"status": st, "len": len(b), "pct_cells": len(pct), "tickers": tick, "links": links,
              "title": (re.search(r"<title>(.*?)</title>", b, re.S) or [None, ""])[1].strip()[:80]}
Path("data/probe.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=1))
