"""구성종목 출처 후보 접속 확인(한 번씩). 결과 → data/probe.json"""
import http.cookiejar, json, re, urllib.request, html as H
from pathlib import Path
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"}
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def get(u):
    with op.open(urllib.request.Request(u, headers=UA), timeout=40) as r:
        return r.read().decode("utf-8", "replace")
out = {}
for k, u in {"funetf_381180": "https://www.funetf.co.kr/product/etf/view/KR7381180009",
             "funetf_381170": "https://www.funetf.co.kr/product/etf/view/KR7381170000",
             "smh": "https://www.vaneck.com/etf/equity/smh/holdings"}.items():
    try:
        b = get(u)
    except Exception as e:  # noqa: BLE001
        out[k] = {"err": f"{type(e).__name__}: {str(e)[:120]}"}; continue
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", b, re.S):
        cells = [H.unescape(re.sub(r"<[^>]+>", " ", c)).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        cells = [re.sub(r"\s+", " ", c) for c in cells if c.strip()]
        if cells and any(re.fullmatch(r"-?\d{1,3}(\.\d+)?%?", c) for c in cells):
            rows.append(cells[:8])
    i = b.find("구성종목")
    out[k] = {"len": len(b), "rows": rows[:40], "ajax": sorted(set(re.findall(r"['\"](/[a-zA-Z0-9_/\-]*(?:pdf|Pdf|PDF|compos|Compos|holding)[a-zA-Z0-9_/\-\.]*)['\"]", b)))[:20],
              "around": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", b[i:i+3000]))[:1200] if i >= 0 else ""}
Path("data/probe.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
