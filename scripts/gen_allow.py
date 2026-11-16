"""실시간 서버가 받아 줄 종목 목록(worker/src/allow.js)을 만들어요.

앱이 실제로 쓰는 종목만 서버가 받아 주게 해서, 아무 종목이나 마구 넣어
외부 시세 사용량을 다 써 버리는 공격을 막아요. 이용자에게는 영향이 없어요.
데이터(구성종목·ETF 목록)가 바뀌면 서버를 올릴 때마다 다시 만들어요.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYM = re.compile(r"^[A-Z][A-Z0-9.\-]{0,9}$")
KRC = re.compile(r"^[0-9A-Z]{6}$")


def load(name):
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def main():
    us, kr = set(), set()
    hold = load("holdings.json").get("etfs", {})
    etfs = load("etfs.json")
    live = load("live.json")
    comp = load("companies.json")
    for code, e in hold.items():
        kr.add(code)
        if e.get("proxy"):
            us.add(e["proxy"])
        for x in e.get("top", []):
            if x.get("ticker"):
                us.add(x["ticker"])
    for g in etfs.get("groups", {}).values():
        if g.get("proxy"):
            us.add(g["proxy"])
    for e in etfs.get("etfs", []):
        if isinstance(e, list) and e:
            kr.add(str(e[0]))
    us |= set(live.get("quotes", {}))
    us |= set(comp.get("co", {}))
    wl = ROOT / "ops" / "watchlist.json"  # Argus가 지켜보는 종목
    if wl.exists():
        us |= {i.get("t", "") for i in json.loads(wl.read_text(encoding="utf-8")).get("items", [])}
    us = sorted(s.upper() for s in us if SYM.match(str(s).upper()))
    kr = sorted(c.upper() for c in kr if KRC.match(str(c).upper()))
    if len(us) < 20 or len(kr) < 5:
        sys.exit(f"종목 목록이 너무 적어요 (미국 {len(us)}, 국내 {len(kr)}). 데이터 파일을 확인하세요.")
    out = ROOT / "worker" / "src" / "allow.js"
    out.write_text(
        "// scripts/gen_allow.py가 만든 파일이에요. 손으로 고치지 마세요.\n"
        "// 앱이 쓰는 종목만 실시간 서버가 받아 줘요.\n"
        f"export const US = new Set({json.dumps(us)});\n"
        f"export const KR = new Set({json.dumps(kr)});\n",
        encoding="utf-8",
    )
    print(f"allow.js: 미국 {len(us)}개, 국내 {len(kr)}개")


if __name__ == "__main__":
    main()
