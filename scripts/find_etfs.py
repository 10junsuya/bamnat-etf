"""공공데이터(금융위원회 증권상품시세)에서 최근 하루치 전체 ETF를 받아, 미국·해외 관련 상품을 순자산·거래대금 순으로 → data/etf_candidates.json"""
import datetime as dt, json, os, urllib.parse, urllib.request
from pathlib import Path
KEY = urllib.parse.unquote(os.environ.get("DATA_GO_KR_API_KEY", "").strip())
URL = "https://apis.data.go.kr/1160100/GetSecuritiesProductInfoService_V2/getETFPriceInfo_V2"
WORDS = ["미국", "글로벌", "테슬라", "엔비디아", "구글", "애플", "마이크로소프트", "아마존", "메타", "팔란티어", "브로드컴", "스페이스X", "빅테크", "나스닥", "S&P"]


def fetch(day):
    rows, page = [], 1
    while True:
        q = {"serviceKey": KEY, "resultType": "json", "numOfRows": 1000, "pageNo": page, "basDt": day}
        with urllib.request.urlopen(urllib.request.Request(URL + "?" + urllib.parse.urlencode(q), headers={"User-Agent": "gnomon"}), timeout=60) as r:
            j = json.loads(r.read().decode())
        b = j["response"]["body"]; items = (b.get("items") or {})
        items = items.get("item", []) if isinstance(items, dict) else items
        items = [items] if isinstance(items, dict) else items
        rows += items
        if len(rows) >= int(b.get("totalCount") or 0) or not items:
            return rows
        page += 1


out = {"error": None, "date": None, "rows": []}
d = dt.date.today()
try:
    for _ in range(10):
        d -= dt.timedelta(days=1)
        if d.weekday() >= 5:
            continue
        rows = fetch(d.strftime("%Y%m%d"))
        if rows:
            out["date"] = d.isoformat(); break
    for i in rows:
        n = i.get("itmsNm") or ""
        if not any(w in n for w in WORDS):
            continue
        out["rows"].append({"code": i.get("srtnCd"), "name": n, "aum_eok": round(float(i.get("nPptTotAmt") or 0) / 1e8),
                            "trade_eok": round(float(i.get("trPrc") or 0) / 1e8, 1), "index": i.get("bssIdxIdxNm"), "nav": i.get("nav"), "close": i.get("clpr")})
    out["rows"].sort(key=lambda x: -x["aum_eok"])
    out["total_etfs"] = len(rows)
except Exception as e:  # noqa: BLE001
    out["error"] = f"{type(e).__name__}: {str(e)[:200]}"
Path("data/etf_candidates.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(out["date"], len(out["rows"]), out["error"])
