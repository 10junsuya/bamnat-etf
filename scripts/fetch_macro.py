"""매크로 지표 실제 값 → data/macro.json (앱에 내장)

미국: FRED(세인트루이스 연준) · 한국: ECOS(한국은행) · 달러 인덱스·발표 후 30분 반응: 야후 파이낸스.
키는 GitHub Secrets 환경변수로만 들어와요.
발표 '예상치(컨센서스)'는 무료 공식 출처가 없어서 여기서 만들지 않아요(앱에서는 '연결 전'으로 표시).
실패한 지표는 기존 값을 지우지 않고 오류만 기록해요.
"""
import datetime as dt
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "macro.json"
KST = ZoneInfo("Asia/Seoul")
FRED_KEY = os.environ.get("FRED_API_KEY", "").strip()
ECOS_KEY = os.environ.get("ECOS_API_KEY", "").strip()


def scrub(t):
    for k in (FRED_KEY, ECOS_KEY):
        if k:
            t = t.replace(k, "***")
    return t


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "gnomon/0.1 (+github.com/10junsuya/gnomon)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def fred(sid, limit=40):
    j = get("https://api.stlouisfed.org/fred/series/observations?" + urllib.parse.urlencode(
        {"series_id": sid, "api_key": FRED_KEY, "file_type": "json", "sort_order": "desc", "limit": limit}))
    obs = [(o["date"], float(o["value"])) for o in j.get("observations", []) if o.get("value") not in (".", None, "")]
    return list(reversed(obs))  # 오래된 것 → 최신


def ecos(code, item, months=40):
    now = dt.datetime.now(KST)
    start = (now - dt.timedelta(days=31 * months)).strftime("%Y%m")
    j = get(f"https://ecos.bok.or.kr/api/StatisticSearch/{ECOS_KEY}/json/kr/1/100/{code}/M/{start}/{now.strftime('%Y%m')}/{item}")
    rows = j.get("StatisticSearch", {}).get("row") or []
    return [(f"{r['TIME'][:4]}-{r['TIME'][4:6]}-01", float(r["DATA_VALUE"])) for r in rows if r.get("DATA_VALUE") not in (None, "")]


ET = ZoneInfo("America/New_York")
UA = {"User-Agent": "Mozilla/5.0 (gnomon-macro)"}


def yahoo(sym, rng, itv, prepost=False):
    """야후 차트: [(유닉스 시각, 종가)]"""
    u = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?range={rng}&interval={itv}"
         + ("&includePrePost=true" if prepost else ""))
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
        res = json.loads(r.read())["chart"]["result"][0]
    ts, cl = res.get("timestamp") or [], res["indicators"]["quote"][0].get("close") or []
    return [(t, c) for t, c in zip(ts, cl) if c is not None]


def fred_release_dates(sid, n=8):
    """이 시리즈가 실린 발표의 최근 발표일(미국 날짜, 최신 → 오래된)"""
    rid = get("https://api.stlouisfed.org/fred/series/release?" + urllib.parse.urlencode(
        {"series_id": sid, "api_key": FRED_KEY, "file_type": "json"}))["releases"][0]["id"]
    j = get("https://api.stlouisfed.org/fred/release/dates?" + urllib.parse.urlencode(
        {"release_id": rid, "api_key": FRED_KEY, "file_type": "json", "sort_order": "desc", "limit": n,
         "include_release_dates_with_no_data": "false"}))
    return [x["date"] for x in j.get("release_dates", [])]


NEXT_SERIES = {"cpi": "CPIAUCSL", "pce": "PCEPI", "ppi": "PPIFIS", "nfp": "PAYEMS", "retail": "RSAFS", "claims": "ICSA",
               "m2": "M2SL", "fomc": "DFEDTARU"}


def fred_next_release(sid):
    """이 시리즈가 실린 발표의 다음 공식 발표일(미국 날짜). FRED가 발표 기관 일정표를 그대로 받아 둬요."""
    rid = get("https://api.stlouisfed.org/fred/series/release?" + urllib.parse.urlencode(
        {"series_id": sid, "api_key": FRED_KEY, "file_type": "json"}))["releases"][0]["id"]
    today = dt.datetime.now(ET).date().isoformat()
    j = get("https://api.stlouisfed.org/fred/release/dates?" + urllib.parse.urlencode(
        {"release_id": rid, "api_key": FRED_KEY, "file_type": "json", "sort_order": "asc", "limit": 10,
         "realtime_start": today, "realtime_end": "9999-12-31", "include_release_dates_with_no_data": "true"}))
    ds = [x["date"] for x in j.get("release_dates", []) if x["date"] >= today]
    return ds[0] if ds else None


def next_releases(ind, errors):
    for k, sid in NEXT_SERIES.items():
        if k not in ind:
            continue
        try:
            d = fred_next_release(sid)
            if d:
                ind[k]["next"] = d
        except Exception as e:  # noqa: BLE001
            errors.append(scrub(f"다음 발표일 {k}: {type(e).__name__}: {e}")[:200])


# 발표 후 30분 반응: 발표 시각(미국 동부 08:30) 직전 5분봉 종가 → 30분 뒤 5분봉 종가
REACT_SYMS = [("ES=F", "pct"), ("^TNX", "pp"), ("DX-Y.NYB", "pct"), ("KRW=X", "won")]  # 앱 순서: S&P500 선물·10년물·달러 인덱스·원/달러
REL_SERIES = {"cpi": "CPIAUCSL", "pce": "PCEPI", "ppi": "PPIFIS", "nfp": "PAYEMS", "retail": "RSAFS", "claims": "ICSA"}


def reactions(ind, errors):
    bars = {}
    for sym, _ in REACT_SYMS:
        try:
            bars[sym] = yahoo(sym, "60d", "5m", True)
        except Exception as e:  # noqa: BLE001
            errors.append(f"반응 {sym}: {type(e).__name__}")
            bars[sym] = []

    def px(sym, t):  # t 시각 이전 마지막 5분봉 종가 (10분 넘게 비면 없음)
        xs = [(a, c) for a, c in bars[sym] if a < t]
        return xs[-1][1] if xs and t - xs[-1][0] <= 900 else None

    now_et = dt.datetime.now(ET)
    for k, sid in REL_SERIES.items():
        if k not in ind:
            continue
        try:
            ds = [d for d in fred_release_dates(sid) if d <= now_et.date().isoformat()]
        except Exception as e:  # noqa: BLE001
            errors.append(scrub(f"발표일 {k}: {type(e).__name__}: {e}")[:200])
            continue
        for d in ds:
            t0 = dt.datetime.fromisoformat(d + "T08:30").replace(tzinfo=ET)
            if t0 + dt.timedelta(minutes=35) > now_et:
                continue  # 오늘 발표인데 아직 30분이 안 지났으면 그 전 발표
            ind[k]["rel"] = t0.isoformat()
            r = []
            for sym, kind in REACT_SYMS:
                a, b = px(sym, t0.timestamp()), px(sym, t0.timestamp() + 1800)
                if a is None or b is None:
                    r.append(None)
                elif kind == "pct":
                    r.append(round((b / a - 1) * 100, 2))
                elif kind == "pp":
                    r.append(round(b - a, 3))
                else:
                    r.append(round(b - a, 1))
            if any(v is not None for v in r):
                ind[k]["react"] = r
                ind[k]["react_src"] = "야후 5분봉 (S&P500 선물 ES=F · 10년물 ^TNX · 달러 인덱스 · 원/달러)"
            else:
                ind[k].pop("react", None)
            break


def ecos_find(errors):
    """ECOS에서 '수출입(통관)' 통계표·항목 찾기 → (표 코드, 항목 코드, 표 이름)"""
    tabs = []
    for a in range(1, 4001, 1000):
        j = get(f"https://ecos.bok.or.kr/api/StatisticTableList/{ECOS_KEY}/json/kr/{a}/{a + 999}")
        rows = j.get("StatisticTableList", {}).get("row") or []
        tabs += rows
        if len(rows) < 1000:
            break
    cand = [t for t in tabs if "수출" in t.get("STAT_NAME", "") and t.get("CYCLE") in ("M", None) and t.get("SRCH_YN") == "Y"]
    cand.sort(key=lambda t: (("통관" not in t["STAT_NAME"]) and ("수출입" not in t["STAT_NAME"]), len(t["STAT_NAME"])))
    print("ECOS 수출 통계표 후보:", [(t["STAT_CODE"], t["STAT_NAME"]) for t in cand[:12]])
    for t in cand[:8]:
        j = get(f"https://ecos.bok.or.kr/api/StatisticItemList/{ECOS_KEY}/json/kr/1/200/{t['STAT_CODE']}")
        items = j.get("StatisticItemList", {}).get("row") or []
        print(" ", t["STAT_CODE"], [(i.get("ITEM_CODE"), i.get("ITEM_NAME"), i.get("CYCLE"), i.get("UNIT_NAME")) for i in items[:10]])
        for i in items:
            nm = (i.get("ITEM_NAME") or "").replace(" ", "")
            if i.get("CYCLE") == "M" and nm in ("수출", "수출(FOB)", "수출금액", "수출액", "수출총액") :
                return t["STAT_CODE"], i["ITEM_CODE"], t["STAT_NAME"]
    raise ValueError("수출 통계를 못 찾았어요")


mon = lambda d: f"{int(d[5:7])}월"
r1 = lambda x, n=1: round(x, n)


def yoy_series(obs):
    """월간 지수 → 전년 대비 %, [(날짜, 값)]"""
    m = {d[:7]: v for d, v in obs}
    out = []
    for d, v in obs:
        y = f"{int(d[:4]) - 1}{d[4:7]}"
        base = m.get(y)
        if base is None:
            # 1년 전 달이 발표되지 않은 경우(예: 2025년 10월 미국 정부 셧다운) 앞뒤 달의 가운데 값으로 채워요
            yy, mm = int(y[:4]), int(y[5:7])
            pv = m.get(f"{yy if mm > 1 else yy - 1}-{(mm - 2) % 12 + 1:02d}")
            nx = m.get(f"{yy if mm < 12 else yy + 1}-{mm % 12 + 1:02d}")
            if pv and nx:
                base = (pv * nx) ** 0.5
                IMPUTED.add(d[:7])
        if base:
            out.append((d, (v / base - 1) * 100))
    return out


IMPUTED = set()


def monthly(key, s, dec=1, src=""):
    """발표형(월간) 지표: 최신 값·이전 값·최근 6개"""
    if len(s) < 2:
        raise ValueError("값이 부족해요")
    note = "1년 전 값이 발표되지 않아 앞뒤 달 가운데 값으로 계산했어요" if s[-1][0][:7] in IMPUTED else ""
    IMPUTED.clear()
    return {"note": note, "a": r1(s[-1][1], dec), "p": r1(s[-2][1], dec), "hist": [r1(v, dec) for _, v in s[-6:]], "ref": mon(s[-1][0]), "asof": s[-1][0], "src": src,
            "series": [[d[:7], r1(v, dec)] for d, v in s[-36:]]}


def market(s, dec=2, src=""):
    """시장 지표: 지금 값·전일 대비·최근 11개"""
    if len(s) < 2:
        raise ValueError("값이 부족해요")
    sp = [r1(v, dec) for _, v in s[-11:]]
    return {"now": sp[-1], "chg": r1(sp[-1] - sp[-2], dec), "spark": sp, "asof": s[-1][0], "src": src,
            "series": [[d, r1(v, dec)] for d, v in s[-756:]]}


def main():
    old = {}
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
        except ValueError:
            old = {}
    ind, errors = dict(old.get("ind", {})), []

    def run(key, fn):
        try:
            ind[key] = fn()
        except Exception as e:  # noqa: BLE001
            errors.append(scrub(f"{key}: {type(e).__name__}: {e}")[:200])

    if FRED_KEY:
        run("cpi", lambda: monthly("cpi", yoy_series(fred("CPIAUCSL", 60)), 1, "FRED CPIAUCSL"))
        run("pce", lambda: monthly("pce", yoy_series(fred("PCEPI", 60)), 1, "FRED PCEPI"))
        run("ppi", lambda: monthly("ppi", yoy_series(fred("PPIFIS", 60)), 1, "FRED PPIFIS"))
        run("m2", lambda: monthly("m2", yoy_series(fred("M2SL", 60)), 1, "FRED M2SL"))

        def nfp():
            o = fred("PAYEMS", 40)
            d = [(o[i][0], (o[i][1] - o[i - 1][1]) / 10) for i in range(1, len(o))]  # 천 명 → 만 명
            return monthly("nfp", d, 1, "FRED PAYEMS (전월 대비 증가)")
        run("nfp", nfp)

        def retail():
            o = fred("RSAFS", 40)
            d = [(o[i][0], (o[i][1] / o[i - 1][1] - 1) * 100) for i in range(1, len(o))]
            return monthly("retail", d, 1, "FRED RSAFS (전월 대비)")
        run("retail", retail)

        def claims():
            o = [(d, v / 10000) for d, v in fred("ICSA", 160)]
            x = monthly("claims", o, 1, "FRED ICSA")
            x["series"] = [[d, r1(v, 1)] for d, v in o[-156:]]
            x["ref"] = f"{int(o[-1][0][5:7])}/{int(o[-1][0][8:10])} 주간"
            return x
        run("claims", claims)

        def fomc():
            o = fred("DFEDTARU", 1200)
            chg = [o[0]] + [o[i] for i in range(1, len(o)) if o[i][1] != o[i - 1][1]]
            x = {"a": r1(o[-1][1], 2), "p": r1(chg[-2][1], 2) if len(chg) >= 2 else r1(o[-1][1], 2),
                 "hist": [r1(v, 2) for _, v in o[-130::26]][-6:], "ref": "", "asof": o[-1][0], "src": "FRED DFEDTARU (목표 범위 상단)",
                 "last_change": chg[-1][0]}
            mm = {}
            for d, v in o:
                if int(d[5:7]) in (1, 3, 5, 6, 7, 9, 10, 12):
                    mm[d[:7]] = r1(v, 2)
            x["series"] = [[k, v] for k, v in sorted(mm.items())][-24:]
            x["hist"] = [v for _, v in x["series"][-6:]]
            x["a"], x["p"] = x["hist"][-1], x["hist"][-2]  # 직전 회의 때 금리
            return x
        run("fomc", fomc)
        run("us10y", lambda: market(fred("DGS10", 800), 2, "FRED DGS10"))
        run("us2y", lambda: market(fred("DGS2", 800), 2, "FRED DGS2"))
        def spread():
            a, b = dict(fred("DGS10", 800)), dict(fred("DGS2", 800))
            return market([(d, a[d] - b[d]) for d in sorted(a) if d in b], 2, "FRED DGS10−DGS2")
        run("spread", spread)
        run("vix", lambda: market(fred("VIXCLS", 800), 1, "FRED VIXCLS (CBOE)"))
        run("wti", lambda: market(fred("DCOILWTICO", 800), 1, "FRED DCOILWTICO (EIA)"))
    else:
        errors.append("FRED_API_KEY 없음")
    if ECOS_KEY:
        def bok():
            o = ecos("722Y001", "0101000", 30)
            chg = [o[0]] + [o[i] for i in range(1, len(o)) if o[i][1] != o[i - 1][1]]
            return {"a": r1(o[-1][1], 2), "p": r1(o[-2][1], 2),
                    "hist": [r1(v, 2) for _, v in o[-6:]], "ref": mon(o[-1][0]), "asof": o[-1][0], "src": "ECOS 722Y001"}
        run("bok", bok)
        run("kcpi", lambda: monthly("kcpi", yoy_series(ecos("901Y009", "0", 52)), 1, "ECOS 901Y009"))

        def export():
            code, item, name = ecos_find(errors)
            x = monthly("export", yoy_series(ecos(code, item, 52)), 1, f"ECOS {code} ({name})")
            x["note"] = (x.get("note") + " · " if x.get("note") else "") + "수출 금액 1년 전 같은 달 대비"
            return x
        run("export", export)
    else:
        errors.append("ECOS_API_KEY 없음")
    run("dxy", lambda: market([(dt.datetime.fromtimestamp(t, ET).date().isoformat(), c) for t, c in yahoo("DX-Y.NYB", "3y", "1d")], 2, "ICE 달러 인덱스 (야후 DX-Y.NYB)"))
    if FRED_KEY:
        try:
            reactions(ind, errors)
        except Exception as e:  # noqa: BLE001
            errors.append(scrub(f"반응: {type(e).__name__}: {e}")[:200])
        next_releases(ind, errors)
    out = {"generated_at_kst": dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M"), "ind": ind, "errors": errors}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"지표 {len(ind)}개 · 오류 {len(errors)}개")
    for e in errors:
        print(" -", e)
    for k, v in ind.items():
        print(k, {x: v[x] for x in v if x not in ("hist", "series")})


if __name__ == "__main__":
    main()
