"""밤사이 예상 계산에 쓰는 숫자 모으기 → data/live.json

GitHub Actions에서 하루 몇 번 돌아요. 키는 GitHub Secrets 환경변수로만 들어오고 파일·로그에 남기지 않아요.
- 미국 시세: Finnhub (구성종목 + 같은 지수 미국 ETF SPY·QQQ·SOXQ)
- 미국 종가 기록: 시세에서 나온 종가/전일 종가를 날짜별로 쌓아요(최근 20거래일)
- 국내 ETF 기준가·종가: 공공데이터포털 금융위원회 증권상품시세 (보통 하루 늦게 올라와요)
- 원/달러: 유럽중앙은행 기준환율(하루 한 번) 최근 기록
앱은 이 파일을 내장해서, 실시간 서버에 못 붙는 곳(미리보기 등)에서도 '언제 기준 숫자인지' 밝히고 보여줘요.
"""
import datetime as dt
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "live.json"
HOLD = ROOT / "data" / "holdings.json"
KST, NY = ZoneInfo("Asia/Seoul"), ZoneInfo("America/New_York")
FINNHUB_KEY = os.environ.get("FINNHUB_API_KEY", "").strip()
DATA_KEY = urllib.parse.unquote(os.environ.get("DATA_GO_KR_API_KEY", "").strip())
ETF_URL = "https://apis.data.go.kr/1160100/GetSecuritiesProductInfoService_V2/getETFPriceInfo_V2"
KR_ETFS = ["381180", "360750", "379800", "360200", "133690", "379810", "0181L0"]
PROXIES = ["SPY", "QQQ", "SOXQ"]
KEEP = 30


def scrub(t):
    for k in (FINNHUB_KEY, DATA_KEY, urllib.parse.quote(DATA_KEY, safe=""), urllib.parse.quote_plus(DATA_KEY)):
        if k:
            t = t.replace(k, "***")
    return t


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "gnomon/0.1 (+github.com/10junsuya/gnomon)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def us_closed_days():
    s = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r"const US_HOL = \[(.*?)\];", s, re.S)
    return {d for d, kind in re.findall(r'\["(\d{4}-\d{2}-\d{2})","[^"]*","(closed|early)"', m.group(1) if m else "") if kind == "closed"}


US_CLOSED = us_closed_days()


def us_trading(d):
    return d.weekday() < 5 and d.isoformat() not in US_CLOSED


def prev_us(d):
    d -= dt.timedelta(days=1)
    while not us_trading(d):
        d -= dt.timedelta(days=1)
    return d


def tickers():
    out = list(PROXIES)
    try:
        h = json.loads(HOLD.read_text(encoding="utf-8"))
        for v in h.get("etfs", {}).values():
            out += [i["ticker"] for i in v.get("top", []) if i.get("ticker")]
    except (OSError, ValueError):
        pass
    seen = []
    for t in out:
        if t not in seen:
            seen.append(t)
    return seen[:60]


def quotes(old, errors):
    q, closes = {}, {k: dict(v) for k, v in old.get("closes", {}).items()}
    if not FINNHUB_KEY:
        errors.append("FINNHUB_API_KEY 없음")
        return old.get("quotes", {}), closes
    now_ny = dt.datetime.now(NY)
    for t in tickers():
        try:
            j = json.loads(get("https://finnhub.io/api/v1/quote?" + urllib.parse.urlencode({"symbol": t, "token": FINNHUB_KEY})))
        except Exception as e:  # noqa: BLE001
            errors.append(scrub(f"{t}: {type(e).__name__}: {e}")[:160])
            continue
        if not j or not j.get("c") or not j.get("t"):
            errors.append(f"{t}: 값 없음")
            continue
        ts = dt.datetime.fromtimestamp(j["t"], dt.timezone.utc).astimezone(NY)
        d = ts.date()
        q[t] = {"p": j["c"], "pc": j.get("pc"), "dp": j.get("dp"), "t": ts.isoformat(timespec="minutes"), "d": d.isoformat()}
        if j.get("pc"):
            closes.setdefault(prev_us(d).isoformat(), {})[t] = j["pc"]
        session_over = now_ny.date() > d or now_ny.hour >= 16
        if session_over:
            closes.setdefault(d.isoformat(), {})[t] = j["c"]
    closes = dict(sorted(closes.items())[-KEEP:])
    return (q or old.get("quotes", {})), closes


def logos(old, errors):
    """회사 로고 주소(Finnhub 회사 정보). 그림은 복사하지 않고 주소만 저장해요."""
    out = dict(old.get("logos", {}))
    if not FINNHUB_KEY:
        return out
    n = 0
    for t in tickers():
        if t in out or n >= 25:
            continue
        n += 1
        try:
            j = json.loads(get("https://finnhub.io/api/v1/stock/profile2?" + urllib.parse.urlencode({"symbol": t, "token": FINNHUB_KEY})))
            u = (j or {}).get("logo") or ""
            out[t] = u if u.startswith("https://") else ""
        except Exception as e:  # noqa: BLE001
            errors.append(scrub(f"로고 {t}: {type(e).__name__}")[:80])
    return out


def kr_navs(old, errors):
    out = {c: list(v) for c, v in old.get("kr", {}).items()}
    if not DATA_KEY:
        errors.append("DATA_GO_KR_API_KEY 없음")
        return out
    begin = (dt.datetime.now(KST) - dt.timedelta(days=40)).strftime("%Y%m%d")
    for code in KR_ETFS:
        try:
            body = get(ETF_URL + "?" + urllib.parse.urlencode({"serviceKey": DATA_KEY, "resultType": "json", "numOfRows": 40, "pageNo": 1, "likeSrtnCd": code, "beginBasDt": begin}))
            j = json.loads(body)
            items = j["response"]["body"].get("items", {}) or {}
            items = items.get("item", []) if isinstance(items, dict) else items
            items = [items] if isinstance(items, dict) else items
            rows = {r["d"]: r for r in out.get(code, [])}
            for i in items:
                if str(i.get("srtnCd", "")).upper() != code.upper():
                    continue
                d = i["basDt"]
                rows[f"{d[:4]}-{d[4:6]}-{d[6:]}"] = {"d": f"{d[:4]}-{d[4:6]}-{d[6:]}", "nav": float(i["nav"]), "close": float(i["clpr"])}
            out[code] = sorted(rows.values(), key=lambda r: r["d"])[-25:]
        except Exception as e:  # noqa: BLE001
            errors.append(scrub(f"{code}: {type(e).__name__}: {e}")[:160])
    return out


def fx(old, errors):
    try:
        start = (dt.date.today() - dt.timedelta(days=45)).isoformat()
        j = json.loads(get(f"https://api.frankfurter.dev/v1/{start}..?base=USD&symbols=KRW"))
        hist = {d: r["KRW"] for d, r in j.get("rates", {}).items()}
        hist = dict(sorted({**old.get("fx", {}).get("hist", {}), **hist}.items())[-KEEP:])
        last = max(hist)
        return {"rate": hist[last], "date": last, "src": "유럽중앙은행 기준환율", "live": False, "hist": hist}
    except Exception as e:  # noqa: BLE001
        errors.append(f"환율: {type(e).__name__}: {str(e)[:120]}")
        return old.get("fx", {})


def main():
    old = {}
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
        except ValueError:
            old = {}
    errors = []
    q, closes = quotes(old, errors)
    out = {"generated_at_kst": dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M"), "quotes": q, "closes": closes,
           "kr": kr_navs(old, errors), "fx": fx(old, errors), "logos": logos(old, errors), "errors": errors[:20]}
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"시세 {len(q)}개 · 종가 {len(closes)}일 · 국내 {sum(1 for v in out['kr'].values() if v)}개 · 오류 {len(errors)}")
    for e in errors:
        print(" -", e)


if __name__ == "__main__":
    main()
