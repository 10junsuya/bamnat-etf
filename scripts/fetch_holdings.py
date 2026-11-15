"""ETF 구성종목(PDF) → data/holdings.json (이후 check_data.py --embed 로 앱에 반영)

1순위: FunETF의 ETF별 구성종목 표 (각 ETF가 실제로 담은 종목·비중)
2순위(실패 시): S&P500은 SPY, 나스닥100은 QQQ 공시 보유종목 / 우주항공TOP10은 신한자산운용 사이트
실패해도 기존 값을 지우지 않고 오류만 기록해요. 하루 한 번만 받아요.
"""
import csv, datetime as dt, html, http.cookiejar, io, json, re, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from etf_list import ETFS, GROUPS, isin  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "holdings.json"
KST = dt.timezone(dt.timedelta(hours=9))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 gnomon/0.2",
      "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"}
OP = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
TOP_PDF = 25    # 비중형은 위에서 25개까지만 하나씩, 나머지 비중은 받은 종목 평균으로 채워요
TOP_INDEX = 15  # 지수형은 위에서 15개만 하나씩 계산하고 나머지는 같은 지수 미국 ETF 움직임에 맞춰요
ISIN_ALIAS = {"US25460G2865": ("TSLL", "Direxion Daily TSLA Bull 2X", "테슬라 2배 ETF")}  # 종목코드 없이 ISIN만 나오는 미국 상장 상품
NAME2TICKER = {"space exploration technologies": "SPCX", "rocket lab": "RKLB", "viasat": "VSAT", "ast spacemobile": "ASTS",
               "firefly aerospace": "FLY", "planet labs": "PL", "intuitive machines": "LUNR", "redwire": "RDW", "blacksky": "BKSY", "satellogic": "SATL"}


def get(url, timeout=40):
    with OP.open(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def num(x):
    try:
        return float(str(x).replace(",", "").replace("%", "").strip())
    except ValueError:
        return None


def funetf(code):
    page = get(f"https://www.funetf.co.kr/product/etf/view/{isin(code)}").decode("utf-8", "replace")
    items, other, asia = [], [], []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        cells = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        cells = [c for c in cells if c]
        if len(cells) < 2:
            continue
        m = re.fullmatch(r"(.+?)\s*\(([A-Z][A-Z0-9.\-/]{0,9})(?:\s+[A-Z]{2})?\)", cells[0])
        w = num(cells[1])
        alias = next((t for k, t in ISIN_ALIAS.items() if k in cells[0]), None)
        if alias and w and w > 0:
            items.append({"ticker": alias[0], "name": alias[1], "ko": alias[2], "weight": w}); continue
        kr_etf = re.search(r"미국(나스닥100|S&P500)", cells[0]) if not m else None
        if kr_etf and w and w > 0:  # 국내 상장 미국 지수 ETF를 담은 경우: 같은 지수 미국 ETF로 계산
            items.append({"ticker": "QQQ" if kr_etf.group(1) == "나스닥100" else "SPY", "name": cells[0], "ko": cells[0].split(" (")[0], "weight": w}); continue
        if not m and w and w > 0 and re.search(r"\((\d{4,6}|[0-9]{3,5}[A-Z]?)\)\s*$", cells[0]) and "KRD" not in cells[0]:
            asia.append([cells[0], w]); continue  # 아시아 거래소 종목: 낮에 거래돼서 밤사이 움직임은 없어요
        if not m or w is None or w <= 0:
            if w is not None and len(other) < 25:
                other.append(cells[:4])  # 종목코드가 없는 줄(옵션·채권·해외 주식 등) — 확인용으로 남겨요
            continue
        nm = m.group(1).split("/")[-1].strip()
        ko = m.group(1).split("/")[0].strip() if "/" in m.group(1) else ""
        items.append({"ticker": m.group(2).replace(".", "-").replace("/", "-"), "name": nm, "ko": ko, "weight": w})
    d = re.search(r"구성종목[^<]{0,40}?(20\d{2}[.\-/]\d{1,2}[.\-/]\d{1,2})", page)
    funetf.other, funetf.asia = other, asia
    for i in items:  # 지수 선물은 같은 지수 미국 ETF로 바꿔서 계산해요
        f = re.fullmatch(r"(NQ|ES)[FGHJKMNQUVXZ]\d", i["ticker"])
        if f:
            i["ticker"], i["ko"] = ("QQQ", "나스닥100 선물") if f.group(1) == "NQ" else ("SPY", "S&P500 선물")
    return (d.group(1) if d else ""), items


def spy():
    import openpyxl  # noqa: PLC0415
    raw = get("https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx")
    rows = list(openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True).active.iter_rows(values_only=True))
    hi = next(i for i, r in enumerate(rows) if r and r[0] == "Name")
    head = [str(h) for h in rows[hi]]
    ix = {k: head.index(k) for k in ("Name", "Ticker", "Weight")}
    return "", [{"ticker": str(r[ix["Ticker"]]).replace(".", "-"), "name": str(r[ix["Name"]]).title(), "weight": num(r[ix["Weight"]])}
                for r in rows[hi + 1:] if r and r[ix["Ticker"]] and num(r[ix["Weight"]])]


def qqq():
    j = json.loads(get("https://dng-api.invesco.com/cache/v1/accounts/en_US/shareclasses/QQQ/holdings/fund?idType=ticker&interval=daily&productType=ETF"))
    return str(j.get("effectiveDate") or ""), [{"ticker": str(h["ticker"]).replace(".", "-"), "name": str(h.get("issuerName") or "").title(),
                                                 "weight": num(h.get("percentageOfTotalNetAssets"))} for h in j.get("holdings", []) if h.get("ticker")]


def soletf_space():
    page = get("https://www.soletf.com/ko/fund/etf/211110?tabIndex=3", 60).decode("utf-8", "replace")
    items = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        cells = [c for c in cells if c]
        if len(cells) < 4 or not cells[-1].endswith("%") or "현금" in cells[-4]:
            continue
        nm, w = cells[-4], num(cells[-1])
        tk = next((t for k, t in NAME2TICKER.items() if k in nm.lower()), None)
        if tk and w:
            items.append({"ticker": tk, "name": nm, "weight": w})
    return "", items


FALLBACK = {"sp": ("SPY 보유종목 공시", spy), "ndx": ("QQQ 보유종목 공시", qqq), "space": ("신한자산운용 구성종목", soletf_space)}


def main():
    old = {}
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
        except ValueError:
            old = {}
    today = dt.datetime.now(KST).strftime("%Y-%m-%d")
    out = {"generated_at_kst": dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M"), "etfs": dict(old.get("etfs", {})), "errors": []}
    cache = {}
    for code, name, g in ETFS:
        G = GROUPS[g]
        src, asof, items = "", "", []
        funetf.other, funetf.asia = [], []
        if G["kind"] == "bond":  # 채권형은 회사가 아니라 국채를 담아서, 같은 지수 미국 ETF(proxy)만 써요
            out["etfs"][code] = {"kind": "bond", "group": g, "name": name, "index": G["name"], "proxy": G["proxy"], "asof": f"{today} 확인",
                                 "n_total": 0, "top": [], "top_weight": 0, "cash_weight": 0, "src": f"채권형 · {G['proxy']}(같은 지수 미국 ETF)로 계산"}
            continue
        try:
            asof, items = funetf(code)
            src = "FunETF 구성종목(PDF)"
            time.sleep(1.5)
        except Exception as e:  # noqa: BLE001
            out["errors"].append(f"{code} FunETF: {type(e).__name__}: {str(e)[:120]}")
        if len(items) < 5 and g in FALLBACK:
            try:
                if g not in cache:
                    cache[g] = FALLBACK[g][1]()
                asof, items = cache[g]
                src = FALLBACK[g][0]
            except Exception as e:  # noqa: BLE001
                out["errors"].append(f"{code} 대체 출처: {type(e).__name__}: {str(e)[:120]}")
        if len(items) < 5:
            out["errors"].append(f"{code} {name}: 구성종목을 못 받아서 이전 값을 그대로 둬요")
            continue
        merged = {}
        for i in items:
            if i["weight"]:
                if i["ticker"] in merged:
                    merged[i["ticker"]]["weight"] += i["weight"]
                else:
                    merged[i["ticker"]] = dict(i)
        items = sorted(merged.values(), key=lambda i: -i["weight"])
        asia_w = round(sum(w for _, w in funetf.asia), 2)
        top = items[:TOP_INDEX] if G["kind"] == "index" else items[:TOP_PDF]
        tw = sum(i["weight"] for i in items)
        out["etfs"][code] = {"kind": G["kind"], "group": g, "name": name, "index": G["name"], "proxy": G["proxy"],
                             "asof": asof or f"{today} 받음", "n_total": len(items),
                             "top": [{"ticker": i["ticker"], "name": i["name"], "ko": i.get("ko", ""), "weight": round(i["weight"], 3)} for i in top],
                             "top_weight": round(sum(i["weight"] for i in top), 2), "cash_weight": round(max(0.0, 100 - tw - asia_w), 2) if G["kind"] == "pdf" else 0,
                             "asia_weight": asia_w if G["kind"] == "pdf" else 0, "asia": [a[0] for a in funetf.asia[:12]] if G["kind"] == "pdf" else [],
                             "rest_weight": round(max(0.0, tw - sum(i["weight"] for i in top)), 2) if G["kind"] == "pdf" else 0,
                             "src": src, "other": funetf.other[:15]}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"ETF {len(out['etfs'])}개, 오류 {len(out['errors'])}개")
    for e in out["errors"]:
        print(" -", e)
    for c, v in out["etfs"].items():
        print(c, v["src"], v["n_total"], v["top_weight"], [(i["ticker"], i["weight"]) for i in v["top"][:4]])


if __name__ == "__main__":
    main()
