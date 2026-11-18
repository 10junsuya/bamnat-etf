"""ETF 분배금 지급 기록 받기 (한국예탁결제원 증권정보포털 SEIBro)

- 출처: SEIBro 'ETF > 권리행사정보 > 분배금지급현황' 화면이 쓰는 조회(로그인 없음, 공개 화면).
- 2026-11-18 대표 결정: 한국투자증권 답(재배포 가능 여부)이 오기 전까지 이 방법을 쓰고,
  가능하다는 답이 오면 한국투자증권 API(예탁원 정보)로 바꾼다.
- 하루 한 번, ETF마다 1번씩(59번) 천천히 조회한다. 실패한 ETF는 이전 기록을 그대로 둔다.
- 결과: data/dist.json  {"updated_kst", "src", "etfs": {code: {"hist": [[기준일, 지급일, 주당분배금, 구분]], "ok": 확인 시각}}}
"""
import json
import re
import sys
import time
import urllib.request
import http.cookiejar
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "dist.json"
KST = timezone(timedelta(hours=9))
PAGE = "https://seibro.or.kr/websquare/control.jsp?w2xPath=/IPORTAL/user/etf/BIP_CNTS06030V.xml&menuNo=174"
API = "https://seibro.or.kr/websquare/engine/proworks/callServletService.jsp"
UA = "Mozilla/5.0 (GNOMON ETF app; daily distribution check)"


def isin(code):
    """국내 종목코드(6자리, 영문 포함 가능) → ISIN. 끝자리는 ISIN 검증 숫자(룬 공식)."""
    base = "KR7" + code + "00"
    digs = "".join(str(int(c, 36)) for c in base)
    tot = 0
    for i, ch in enumerate(reversed(digs)):
        n = int(ch)
        if i % 2 == 0:
            n *= 2
            if n > 9:
                n -= 9
        tot += n
    return base + str((10 - tot % 10) % 10)


def ymd(s):
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}" if s and len(s) == 8 and s.isdigit() else None


def query(opener, isn, frm, to):
    body = (f'<reqParam action="exerInfoDtramtPayStatPlist" task="ksd.safe.bip.cnts.etf.process.EtfExerInfoPTask">'
            f'<START_PAGE value="1"/><END_PAGE value="200"/><etf_sort_cd value=""/><etf_big_sort_cd value=""/>'
            f'<isin value="{isn}"/><mngco_custno value=""/><RGT_RSN_DTAIL_SORT_CD value=""/>'
            f'<fromRGT_STD_DT value="{frm}"/><toRGT_STD_DT value="{to}"/></reqParam>').encode("utf-8")
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "Content-Type": "application/xml; charset=UTF-8", "User-Agent": UA, "Referer": PAGE})
    with opener.open(req, timeout=25) as r:
        x = r.read().decode("utf-8", "replace")
    if "<vector" not in x:
        raise RuntimeError("응답 모양이 달라요")
    rows = []
    for blk in re.findall(r"<result>(.*?)</result>", x, re.S):
        f = dict(re.findall(r'<(\w+) value="([^"]*)"', blk))
        if f.get("ISIN") != isn:
            continue
        rec, pay = ymd(f.get("RGT_STD_DT")), ymd(f.get("TH1_PAY_TERM_BEGIN_DT"))
        try:
            amt = float(f.get("ESTM_STDPRC") or "")
        except ValueError:
            continue
        if not rec or amt < 0:
            continue
        kind = "청산" if "청산" in f.get("RGT_RSN_DTAIL_NM", "") else "이익"
        rows.append([rec, pay, int(amt) if amt == int(amt) else amt, kind])
    rows.sort(key=lambda r: r[0])
    return rows


def main():
    etfs = json.loads((ROOT / "data" / "etfs.json").read_text(encoding="utf-8"))["etfs"]
    old = {}
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8")).get("etfs", {})
        except Exception:
            old = {}
    now = datetime.now(KST)
    frm = (now - timedelta(days=3 * 365 + 5)).strftime("%Y%m%d")
    to = (now + timedelta(days=60)).strftime("%Y%m%d")
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    try:
        opener.open(urllib.request.Request(PAGE, headers={"User-Agent": UA}), timeout=25).read()
    except Exception as e:
        print("첫 화면 열기 실패(계속 진행):", e)
    out, ok, fail = {}, 0, []
    for code, name, _g in etfs:
        prev = old.get(code)
        for attempt in range(2):
            try:
                rows = query(opener, isin(code), frm, to)
                out[code] = {"hist": rows, "ok": now.strftime("%Y-%m-%d %H:%M")}
                ok += 1
                break
            except Exception as e:
                if attempt == 1:
                    fail.append(f"{code} {name}: {e}")
                    if prev:
                        out[code] = prev  # 실패하면 이전 기록 그대로
                time.sleep(2)
        time.sleep(0.6)
    print(f"분배금: 성공 {ok} · 실패 {len(fail)} / {len(etfs)}")
    for f in fail:
        print("  실패:", f)
    if ok == 0:
        print("모두 실패 — 파일을 바꾸지 않아요")
        sys.exit(1 if not OUT.exists() else 0)
    data = {"updated_kst": now.strftime("%Y-%m-%d %H:%M"),
            "src": [["한국예탁결제원 SEIBro · 분배금지급현황", "https://seibro.or.kr/websquare/control.jsp?w2xPath=/IPORTAL/user/etf/BIP_CNTS06030V.xml&menuNo=174"]],
            "fail": len(fail), "etfs": out}
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
