"""실제 데이터 연결 첫 테스트.

GitHub Actions에서 실행돼요. API 키는 GitHub Secrets에서 환경변수로만 들어오고,
결과 파일과 로그에는 키를 절대 남기지 않아요.

결과: data/test.json
"""
import datetime as dt
import json
import os
import urllib.error
import urllib.parse
import urllib.request

FINNHUB_KEY = os.environ.get("FINNHUB_API_KEY", "").strip()
DATA_KEY = os.environ.get("DATA_GO_KR_API_KEY", "").strip()

US_TICKERS = ["NVDA", "AAPL", "MSFT", "AVGO", "QQQ", "SPY", "SOXX"]
KR_ETFS = {
    "381180": "TIGER 미국필라델피아반도체나스닥",
    "360750": "TIGER 미국S&P500",
    "379800": "KODEX 미국S&P500",
    "360200": "ACE 미국S&P500",
    "133690": "TIGER 미국나스닥100",
    "379810": "KODEX 미국나스닥100",
    "0181L0": "SOL 미국우주항공TOP10",
}
ETF_URLS = [
    "https://apis.data.go.kr/1160100/service/GetSecuritiesProductInfoService/getETFPriceInfo",
    "https://apis.data.go.kr/1160100/service/GetSecuritiesProductInfoService/getETFPriceInfo_V2",
    "https://apis.data.go.kr/1160100/service/GetSecuritiesProductInfoService_V2/getETFPriceInfo_V2",
]
KST = dt.timezone(dt.timedelta(hours=9))


def scrub(text):
    """혹시라도 키가 섞이면 지워요."""
    for k in (FINNHUB_KEY, DATA_KEY, urllib.parse.quote(DATA_KEY, safe="")):
        if k:
            text = text.replace(k, "***")
    return text


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "bamnat-etf/0.1 (+github.com/10junsuya/bamnat-etf)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def finnhub():
    out = {}
    if not FINNHUB_KEY:
        return {"error": "FINNHUB_API_KEY 없음"}
    for s in US_TICKERS:
        try:
            st, body = get("https://finnhub.io/api/v1/quote?" + urllib.parse.urlencode({"symbol": s, "token": FINNHUB_KEY}))
            if st != 200:
                out[s] = {"status": st, "body": scrub(body[:200])}
                continue
            q = json.loads(body)
            out[s] = {"price": q.get("c"), "prev_close": q.get("pc"), "change_pct": q.get("dp"),
                      "time_utc": dt.datetime.fromtimestamp(q["t"], dt.timezone.utc).isoformat() if q.get("t") else None}
        except Exception as e:  # noqa: BLE001
            out[s] = {"error": scrub(f"{type(e).__name__}: {e}")[:200]}
    return out


def etf_prices():
    if not DATA_KEY:
        return {"error": "DATA_GO_KR_API_KEY 없음"}
    begin = (dt.datetime.now(KST) - dt.timedelta(days=14)).strftime("%Y%m%d")
    tried, working = [], None
    rows = {}
    for code, name in KR_ETFS.items():
        urls = [working] if working else ETF_URLS
        for base in urls:
            params = {"serviceKey": DATA_KEY, "resultType": "json", "numOfRows": 20, "pageNo": 1,
                      "likeSrtnCd": code, "beginBasDt": begin}
            try:
                st, body = get(base + "?" + urllib.parse.urlencode(params))
            except Exception as e:  # noqa: BLE001
                tried.append({"url": base, "error": scrub(f"{type(e).__name__}: {e}")[:200]})
                continue
            try:
                j = json.loads(body)
            except ValueError:
                tried.append({"url": base, "status": st, "body": scrub(body[:300])})
                continue
            header = j.get("response", {}).get("header", {})
            if header.get("resultCode") != "00":
                tried.append({"url": base, "status": st, "header": header})
                continue
            working = base
            items = j["response"]["body"].get("items", {}) or {}
            items = items.get("item", []) if isinstance(items, dict) else items
            if isinstance(items, dict):
                items = [items]
            mine = [i for i in items if str(i.get("srtnCd", "")).upper() == code.upper()]
            mine.sort(key=lambda i: i.get("basDt", ""), reverse=True)
            if not mine:
                rows[code] = {"name": name, "error": "결과 없음"}
                break
            last = mine[0]
            rows[code] = {
                "name": last.get("itmsNm", name),
                "date": last.get("basDt"),
                "close": last.get("clpr"),
                "nav": last.get("nav"),
                "change_pct": last.get("fltRt"),
                "index": last.get("bssIdxIdxNm"),
                "fields": sorted(last.keys()),
            }
            break
        else:
            rows[code] = {"name": name, "error": "모든 주소 실패"}
    return {"working_url": working, "tried": tried[:6], "etfs": rows}


def fx():
    out = {}
    for url in ("https://api.frankfurter.dev/v1/latest?base=USD&symbols=KRW",
                "https://api.frankfurter.app/latest?from=USD&to=KRW"):
        try:
            st, body = get(url)
            if st == 200:
                j = json.loads(body)
                out = {"source": url.split("/")[2], "date": j.get("date"), "usdkrw": j.get("rates", {}).get("KRW")}
                break
            out = {"status": st}
        except Exception as e:  # noqa: BLE001
            out = {"error": f"{type(e).__name__}: {e}"[:200]}
    return out


def main():
    result = {
        "generated_at_kst": dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S"),
        "finnhub_us_quotes": finnhub(),
        "krx_etf_prices": etf_prices(),
        "fx_usdkrw_ecb": fx(),
    }
    os.makedirs("data", exist_ok=True)
    text = scrub(json.dumps(result, ensure_ascii=False, indent=2))
    with open("data/test.json", "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
