"""국내 ETF 구성종목(PDF, 자산구성내역) 받아오기 → data/holdings.json

ETF는 매일 장 마감 뒤 구성종목(PDF)을 공개해요. 한국거래소 정보데이터시스템에서 받아요.
첫 단계라 받아지는지 시험하는 용도도 겸해요. 결과·오류를 data/holdings.json 에 남겨요.
"""
import datetime as dt
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "holdings.json"
KST = dt.timezone(dt.timedelta(hours=9))
ETFS = {
    "381180": "TIGER 미국필라델피아반도체나스닥",
    "360750": "TIGER 미국S&P500",
    "379800": "KODEX 미국S&P500",
    "360200": "ACE 미국S&P500",
    "133690": "TIGER 미국나스닥100",
    "379810": "KODEX 미국나스닥100",
    "0181L0": "SOL 미국우주항공TOP10",
}
KRX = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
HEAD = {
    "User-Agent": "Mozilla/5.0 (gnomon; +https://github.com/10junsuya/gnomon)",
    "Referer": "https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201030108",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
}


def post(params, timeout=25):
    req = urllib.request.Request(KRX, data=urllib.parse.urlencode(params).encode(), headers=HEAD, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def num(x):
    try:
        return float(str(x).replace(",", ""))
    except ValueError:
        return None


def isin_of(code):
    st, body = post({"bld": "dbms/comm/finder/finder_secuprodisu", "mktsel": "ETF", "searchText": code})
    j = json.loads(body)
    for b in j.get("block1", []):
        if b.get("short_code") == code:
            return b.get("full_code"), b.get("codeName")
    return None, None


def pdf(isin, day):
    st, body = post({"bld": "dbms/MDC/STAT/standard/MDCSTAT05001", "locale": "ko_KR", "tboxisuCd_finder_secuprodisu1_0": "",
                     "isuCd": isin, "isuCd2": "", "codeNmisuCd_finder_secuprodisu1_0": "", "param1isuCd_finder_secuprodisu1_0": "",
                     "trdDd": day, "share": "1", "money": "1", "csvxls_isNo": "false"})
    j = json.loads(body)
    return j.get("output", [])


def main():
    now = dt.datetime.now(KST)
    out = {"generated_at_kst": now.strftime("%Y-%m-%d %H:%M:%S"), "source": "한국거래소 정보데이터시스템 ETF PDF", "etfs": {}, "errors": []}
    for code, name in ETFS.items():
        try:
            isin, nm = isin_of(code)
            if not isin:
                out["errors"].append(f"{code}: ISIN을 찾지 못했어요")
                continue
            rows, day_used = [], None
            for back in range(0, 7):
                day = (now - dt.timedelta(days=back)).strftime("%Y%m%d")
                rows = pdf(isin, day)
                if rows:
                    day_used = day
                    break
                time.sleep(0.5)
            if not rows:
                out["errors"].append(f"{code}: 최근 7일 PDF가 비어 있어요")
                continue
            keys = sorted(rows[0].keys())
            items = []
            for r in rows:
                items.append({
                    "code": r.get("COMPST_ISU_CD") or r.get("ISU_CD"),
                    "name": r.get("COMPST_ISU_NM") or r.get("ISU_NM"),
                    "qty": num(r.get("COMPST_ISU_CU1_SHRS") or r.get("COMPST_AMT")),
                    "value_krw": num(r.get("VALU_AMT")),
                    "weight_pct": num(r.get("COMPST_RTO")),
                })
            out["etfs"][code] = {"name": nm or name, "isin": isin, "date": day_used, "n": len(items), "raw_keys": keys, "items": items}
        except Exception as e:  # noqa: BLE001
            out["errors"].append(f"{code}: {type(e).__name__}: {str(e)[:200]}")
        time.sleep(1)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"ETF {len(out['etfs'])}개, 오류 {len(out['errors'])}개")
    for e in out["errors"]:
        print(" -", e)


if __name__ == "__main__":
    main()
