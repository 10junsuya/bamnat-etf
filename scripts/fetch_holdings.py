"""ETF 구성종목 받아오기 → data/holdings.json (이후 check_data.py --embed 로 앱에 반영)

- 지수형(S&P500, 나스닥100, 필라델피아 반도체): 같은 지수를 따르는 미국 ETF의 공개 보유종목 상위 비중을 써요.
  국내 ETF가 같은 지수를 따라가므로 비중이 거의 같아요. 예상 등락률은 그 미국 ETF 시세로 계산해요.
- 테마형(SOL 미국우주항공TOP10): 운용사(신한자산운용)가 매일 공개하는 구성종목(PDF)을 그대로 써요.
실패해도 기존 값을 지우지 않고 오류만 기록해요.
"""
import csv
import datetime as dt
import html
import io
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "holdings.json"
KST = dt.timezone(dt.timedelta(hours=9))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 gnomon/0.1",
      "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"}
TOP = 15

GROUPS = {
    "sp": {"proxy": "SPY", "index": "S&P 500", "codes": ["360750", "379800", "360200"]},
    "ndx": {"proxy": "QQQ", "index": "나스닥100", "codes": ["133690", "379810"]},
    "sox": {"proxy": "SOXQ", "index": "필라델피아 반도체", "codes": ["381180"]},
}
SPACE = {"code": "0181L0", "url": "https://www.soletf.com/ko/fund/etf/211110?tabIndex=3"}
NAME2TICKER = {
    "space exploration technologies": "SPCX", "rocket lab": "RKLB", "viasat": "VSAT", "ast spacemobile": "ASTS",
    "firefly aerospace": "FLY", "planet labs": "PL", "intuitive machines": "LUNR", "redwire": "RDW",
    "blacksky": "BKSY", "satellogic": "SATL", "iridium": "IRDM", "echostar": "SATS", "karman": "KRMN",
}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def num(x):
    try:
        return float(str(x).replace(",", "").replace("%", "").strip())
    except ValueError:
        return None


def spy():
    """SSGA SPY 일일 보유종목(xlsx)."""
    import openpyxl  # noqa: PLC0415
    raw = get("https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx")
    ws = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True).active
    rows = list(ws.iter_rows(values_only=True))
    asof = next((str(r[1]) for r in rows[:6] if r and r[0] and "Holdings" in str(r[0])), "")
    hi = next(i for i, r in enumerate(rows) if r and r[0] == "Name")
    head = [str(h) for h in rows[hi]]
    ix = {k: head.index(k) for k in ("Name", "Ticker", "Weight")}
    items = []
    for r in rows[hi + 1:]:
        if not r or not r[ix["Ticker"]] or r[ix["Weight"]] in (None, "-"):
            continue
        items.append({"ticker": str(r[ix["Ticker"]]).replace(".", "-"), "name": str(r[ix["Name"]]).title(), "weight": num(r[ix["Weight"]])})
    return asof, items


def invesco(ticker):
    """Invesco 보유종목: JSON API → CSV 다운로드 순서로 시도. 실패하면 응답 앞부분을 오류에 남겨요."""
    notes = []
    for interval in ("daily", "monthly"):
      try:
        raw = get(f"https://dng-api.invesco.com/cache/v1/accounts/en_US/shareclasses/{ticker}/holdings/fund?idType=ticker&interval={interval}&productType=ETF")
        j = json.loads(raw)
        hs = j.get("holdings") or []
        items = [{"ticker": str(h.get("ticker") or "").replace(".", "-"), "name": str(h.get("issuerName") or h.get("name") or "").title(),
                  "weight": num(h.get("percentageOfTotalNetAssets") if h.get("percentageOfTotalNetAssets") is not None else h.get("weight"))}
                 for h in hs if h.get("ticker")]
        items = [i for i in items if i["weight"] is not None]
        if items:
            return str(j.get("effectiveDate") or j.get("asOfDate") or ""), items
        notes.append(f"json-{interval}:" + raw[:160].decode("utf-8", "replace"))
      except Exception as e:  # noqa: BLE001
        notes.append(f"json-{interval}:{type(e).__name__}:{str(e)[:80]}")
    raw = get(f"https://www.invesco.com/us/financial-products/etfs/holdings/main/holdings/0?audienceType=Investor&action=download&ticker={ticker}").decode("utf-8-sig", "replace")
    lines = raw.splitlines()
    hi = next((i for i, l in enumerate(lines[:15]) if "Weight" in l and ("Ticker" in l or "ticker" in l)), None)
    items, asof = [], ""
    if hi is not None:
        for r in csv.DictReader(io.StringIO("\n".join(lines[hi:]))):
            r = {(k or "").strip(): (v or "").strip() for k, v in r.items()}
            t = r.get("Holding Ticker") or r.get("Ticker") or ""
            w = num(r.get("Weight") or "")
            if not t or w is None:
                continue
            asof = asof or r.get("Date", "")
            items.append({"ticker": t.replace(".", "-"), "name": r.get("Name", "").title(), "weight": w})
    if not items:
        notes.append("csv:" + raw[:160].replace("\n", " | "))
        raise ValueError(" / ".join(notes))
    return asof, items


def sox_fallback(err):
    """SOXQ가 안 되면: 나스닥 지수 비중 파일 → TIGER 운용사 페이지 순서로 시도."""
    import openpyxl  # noqa: PLC0415
    notes = [str(err)[:120]]
    today = dt.datetime.now(KST).date()
    for back in range(1, 6):
        d = (today - dt.timedelta(days=back)).isoformat()
        try:
            raw = get(f"https://indexes.nasdaqomx.com/Index/ExportWeightings/SOX?tradeDate={d}T00:00:00.000&timeOfDay=SOD")
            try:
                ws = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True).active
                rows = [r for r in ws.iter_rows(values_only=True)]
            except Exception as e2:  # noqa: BLE001
                raise ValueError(f"엑셀 아님({type(e2).__name__}) 길이 {len(raw)} 앞부분 {raw[:200]!r}")
            hi = next((i for i, r in enumerate(rows) if r and any(str(c).strip().lower() in ("symbol", "ticker", "security symbol") for c in r if c)), None)
            if hi is None:
                raise ValueError(f"머리줄 못 찾음 · 행 {len(rows)}개 · 앞 6행 {[r for r in rows[:6]]!r}"[:600])
            head = [str(c or "").strip().lower() for c in rows[hi]]
            ti = next(i for i, h in enumerate(head) if h in ("symbol", "ticker"))
            ni = next((i for i, h in enumerate(head) if "name" in h), ti)
            wi = next(i for i, h in enumerate(head) if "weight" in h)
            items = []
            for r in rows[hi + 1:]:
                if r and r[ti] and num(r[wi]) is not None:
                    w = num(r[wi]); w = w * 100 if w <= 1 else w
                    items.append({"ticker": str(r[ti]).strip(), "name": str(r[ni] or "").title(), "weight": w})
            if items:
                return d, items, "나스닥 SOX 지수 비중"
            notes.append(f"nasdaq {d}: 행 없음")
        except Exception as e:  # noqa: BLE001
            notes.append(f"nasdaq {d}: {type(e).__name__}:{str(e)[:600]}")
            if back >= 2:
                break
    try:
        page = get("https://investments.miraeasset.com/tigeretf/ko/product/search/detail/index.do?ksdFund=KR7381180009", timeout=40).decode("utf-8", "replace")
        items = table_rows(page)
        if len(items) >= 10:
            return "", items, "미래에셋자산운용 구성종목(PDF)"
        paths = sorted(set(re.findall(r"[\"'](/tigeretf/[^\"'?#]+\.(?:ajax|do|json))", page)))[:12]
        notes.append(f"mirae: 표 {len(items)}행, 길이 {len(page)}, 경로 {paths}")
    except Exception as e:  # noqa: BLE001
        notes.append(f"mirae: {type(e).__name__}:{str(e)[:60]}")
    raise ValueError(" / ".join(notes))


def table_rows(page):
    out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        cells = [c for c in cells if c]
        if len(cells) >= 3 and re.fullmatch(r"\d{1,2}\.\d{1,2}%?", cells[-1]):
            out.append({"ticker": None, "name": cells[0] if not re.fullmatch(r"\d+", cells[0]) else cells[1], "weight": num(cells[-1])})
    return out


def space():
    page = get(SPACE["url"], timeout=60).decode("utf-8", "replace")
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S)
    items, cash = [], 0.0
    for tr in rows:
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        cells = [c for c in cells if c != ""]
        if len(cells) < 4 or not cells[-1].endswith("%"):
            continue
        name, qty, val, w = cells[-4], num(cells[-3]), num(cells[-2]), num(cells[-1])
        if w is None:
            continue
        if "현금" in name:
            cash += w
            continue
        tk = next((t for k, t in NAME2TICKER.items() if k in name.lower()), None)
        items.append({"ticker": tk, "name": name, "qty": qty, "value_krw": val, "weight": w})
    d = re.search(r"(20\d{2}[.\-]\d{2}[.\-]\d{2})", page)
    return (d.group(1) if d else ""), items, cash


def main():
    old = {}
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
        except ValueError:
            old = {}
    out = {"generated_at_kst": dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M"), "etfs": dict(old.get("etfs", {})), "errors": []}
    for g, cfg in GROUPS.items():
        try:
            src = f"{cfg['proxy']} 보유종목 공시"
            if cfg["proxy"] == "SPY":
                asof, items = spy()
            else:
                try:
                    asof, items = invesco(cfg["proxy"])
                except Exception as e:  # noqa: BLE001
                    if g != "sox":
                        raise
                    asof, items, src = sox_fallback(e)
            items = sorted([i for i in items if i["weight"]], key=lambda i: -i["weight"])
            if len(items) < 10:
                raise ValueError(f"보유종목이 {len(items)}개뿐이에요")
            top = items[:TOP]
            entry = {"kind": "index", "index": cfg["index"], "proxy": cfg["proxy"], "asof": asof, "n_total": len(items),
                     "top": [{"ticker": i["ticker"], "name": i["name"], "weight": round(i["weight"], 3)} for i in top],
                     "top_weight": round(sum(i["weight"] for i in top), 2),
                     "src": src}
            for c in cfg["codes"]:
                out["etfs"][c] = entry
        except Exception as e:  # noqa: BLE001
            out["errors"].append(f"{g}({cfg['proxy']}): {type(e).__name__}: {str(e)[:2000]}")
    try:
        asof, items, cash = space()
        if len(items) < 5:
            raise ValueError(f"구성종목이 {len(items)}개뿐이에요")
        miss = [i["name"] for i in items if not i["ticker"]]
        if miss:
            out["errors"].append("우주항공: 티커를 모르는 종목 " + ", ".join(miss))
        out["etfs"][SPACE["code"]] = {"kind": "pdf", "index": "KEDI 미국우주항공TOP10", "asof": asof, "n_total": len(items),
                                     "top": [{"ticker": i["ticker"], "name": i["name"], "weight": i["weight"]} for i in sorted(items, key=lambda i: -i["weight"])],
                                     "cash_weight": round(cash, 2), "src": "신한자산운용 구성종목(PDF)"}
    except Exception as e:  # noqa: BLE001
        out["errors"].append(f"우주항공(soletf): {type(e).__name__}: {str(e)[:2000]}")
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"ETF {len(out['etfs'])}개, 오류 {len(out['errors'])}개")
    for e in out["errors"]:
        print(" -", e)


if __name__ == "__main__":
    main()
