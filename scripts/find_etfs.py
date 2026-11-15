"""공공데이터(금융위원회 증권상품시세)에서 이름으로 ETF를 찾아 종목코드·순자산·기초지수를 확인 → data/etf_candidates.json"""
import datetime as dt, json, os, urllib.parse, urllib.request
from pathlib import Path
KEY = urllib.parse.unquote(os.environ.get("DATA_GO_KR_API_KEY", "").strip())
URL = "https://apis.data.go.kr/1160100/GetSecuritiesProductInfoService_V2/getETFPriceInfo_V2"
WORDS = ["미국S&P500", "미국나스닥100", "미국배당다우존스", "미국테크TOP10", "미국빅테크", "미국반도체", "필라델피아", "우주"]
out, seen = [], set()
begin = (dt.date.today() - dt.timedelta(days=10)).strftime("%Y%m%d")
for w in WORDS:
    q = {"serviceKey": KEY, "resultType": "json", "numOfRows": 300, "pageNo": 1, "likeItmsNm": w, "beginBasDt": begin}
    try:
        with urllib.request.urlopen(urllib.request.Request(URL + "?" + urllib.parse.urlencode(q), headers={"User-Agent": "gnomon"}), timeout=40) as r:
            j = json.loads(r.read().decode())
        items = j["response"]["body"].get("items", {}) or {}
        items = items.get("item", []) if isinstance(items, dict) else items
        items = [items] if isinstance(items, dict) else items
    except Exception as e:  # noqa: BLE001
        out.append({"word": w, "error": f"{type(e).__name__}: {str(e)[:150]}"}); continue
    latest = {}
    for i in items:
        c = i.get("srtnCd")
        if c not in latest or i["basDt"] > latest[c]["basDt"]:
            latest[c] = i
    for c, i in latest.items():
        if c in seen: continue
        seen.add(c)
        out.append({"word": w, "code": c, "name": i.get("itmsNm"), "date": i.get("basDt"), "aum_eok": round(float(i.get("nPptTotAmt") or 0) / 1e8),
                    "mcap_eok": round(float(i.get("mrktTotAmt") or 0) / 1e8), "index": i.get("bssIdxIdxNm"), "nav": i.get("nav"), "close": i.get("clpr")})
out.sort(key=lambda x: (x.get("word", ""), -(x.get("aum_eok") or 0)))
Path("data/etf_candidates.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(len(out))
