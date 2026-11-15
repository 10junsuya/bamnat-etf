"""data/*.json 검사 (Quill이 고친 뒤, 그리고 GitHub에서 자동으로 돌아요).

python3 scripts/check_data.py          → 검사만
python3 scripts/check_data.py --embed  → 검사 통과 시 index.html 안의 데이터 블록을 data/*.json 으로 갱신

문제가 있으면 무엇이 왜 틀렸는지 한국어로 출력하고 실패(1)로 끝나요.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "index.html"
FILES = {"d-events": "data/events.json", "d-missions": "data/missions.json", "d-money": "data/money.json",
         "d-holdings": "data/holdings.json", "d-live": "data/live.json"}
OPTIONAL = {"d-holdings", "d-live"}  # 자동 수집 파일: 없으면 빈 값으로 넣어요
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL = re.compile(r"^https?://\S+$")
TYPES = {"earn", "launch", "land", "event"}
errors = []


def err(where, msg):
    errors.append(f"[{where}] {msg}")


def tickers():
    s = APP.read_text(encoding="utf-8")
    i = s.find("const STOCKS = {")
    j = s.find("\n};", i)
    return set(re.findall(r"\b([A-Z]{1,6})\s*:\s*\[", s[i:j]))


def check_src(where, src):
    if not isinstance(src, list) or not src:
        err(where, "출처(src)가 비어 있어요. 공식 출처 링크가 꼭 있어야 해요.")
        return
    for x in src:
        if not (isinstance(x, list) and len(x) == 2 and isinstance(x[0], str) and URL.match(str(x[1]))):
            err(where, f"출처 형식이 틀렸어요: {x!r} (예: [\"이름\", \"https://...\"])")


def check_events(ev, known):
    if not isinstance(ev, list):
        return err("events", "목록([ ])이어야 해요.")
    seen = set()
    for n, e in enumerate(ev):
        w = f"events #{n} {e.get('t')}:{e.get('d')}" if isinstance(e, dict) else f"events #{n}"
        if not isinstance(e, dict):
            err(w, "항목이 객체({ })가 아니에요.")
            continue
        if not DATE.match(str(e.get("d", ""))):
            err(w, "날짜(d)는 YYYY-MM-DD 형식이어야 해요.")
        if e.get("t") not in known:
            err(w, f"티커(t) {e.get('t')!r} 가 앱 종목 목록(STOCKS)에 없어요.")
        if e.get("type") not in TYPES:
            err(w, f"종류(type)는 {sorted(TYPES)} 중 하나여야 해요.")
        if not str(e.get("title", "")).strip():
            err(w, "제목(title)이 비어 있어요.")
        key = (e.get("t"), e.get("d"))
        if key in seen:
            err(w, "같은 회사·날짜 일정이 두 번 들어 있어요.")
        seen.add(key)
        c = e.get("card")
        if c:
            if c.get("real") and not DATE.match(str(c.get("asof", ""))):
                err(w, "실제 결과 카드(real)는 기준일(asof)이 있어야 해요.")
            check_src(w, c.get("src"))
            for t in c.get("tiles", []):
                if not (isinstance(t, list) and len(t) >= 3):
                    err(w, f"타일 형식이 틀렸어요: {t!r}")


def check_missions(ms, ev, art_counts):
    keys = {f"{e.get('t')}:{e.get('d')}" for e in ev if isinstance(e, dict)}
    for k, m in ms.items():
        w = f"missions {k}"
        if k not in keys:
            err(w, "events.json 에 같은 회사·날짜 일정이 없어요.")
        if not isinstance(m.get("ok"), bool):
            err(w, "ok 는 true(완료) 또는 false(예정)여야 해요.")
        steps = m.get("steps")
        if not (isinstance(steps, list) and steps and all(isinstance(s, list) and len(s) == 3 for s in steps)):
            err(w, "단계(steps)는 [시각, 제목, 설명] 목록이어야 해요.")
        elif k in art_counts and art_counts[k] and art_counts[k] != len(steps):
            err(w, f"단계 수({len(steps)})가 그림 수({art_counts[k]})와 달라요. 단계를 늘리거나 줄이면 그림도 같이 바꿔야 해서 사람 승인이 필요해요.")
        if len(m.get("tags", [])) not in (0, len(steps or [])):
            err(w, "tags 수가 단계 수와 달라요.")


def check_money(mo, known):
    for t, m in mo.items():
        w = f"money {t}"
        if t not in known:
            err(w, "앱 종목 목록에 없는 티커예요.")
        if not str(m.get("p", "")).strip():
            err(w, "기간(p)이 비어 있어요.")
        segs = m.get("segs")
        if not (isinstance(segs, list) and segs):
            err(w, "사업(segs)이 비어 있어요.")
            continue
        for s in segs:
            if not (isinstance(s, list) and len(s) >= 2 and isinstance(s[0], str) and isinstance(s[1], (int, float)) and s[1] > 0):
                err(w, f"사업 형식이 틀렸어요: {s!r} (예: [\"데이터센터\", 89000, \"설명\"])")
        if m.get("pct") and abs(sum(s[1] for s in segs if isinstance(s, list) and len(s) > 1 and isinstance(s[1], (int, float))) - 100) > 2:
            err(w, "비율만 쓰는 경우(pct) 합이 100% 근처여야 해요.")
        if not str(m.get("note", "")).strip():
            err(w, "한 줄 설명(note)이 비어 있어요.")
        check_src(w, m.get("src"))


def art_frame_counts():
    s = APP.read_text(encoding="utf-8")
    i = s.find("const MISSION_ART = ")
    if i < 0:
        return {}
    j = s.find(";\n", i)
    try:
        art = json.loads(s[i + len("const MISSION_ART = "):j])
    except ValueError:
        return {}
    return {k: len(v) for k, v in art.items()}


def block(id_, obj):
    txt = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/json" id="{id_}">{txt}</script>'


def main():
    embed = "--embed" in sys.argv
    data = {}
    for id_, f in FILES.items():
        try:
            data[id_] = json.loads((ROOT / f).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            if id_ in OPTIONAL:
                data[id_] = {}
            else:
                err(f, f"JSON을 읽을 수 없어요: {e}")
    if not errors:
        known = tickers()
        check_events(data["d-events"], known)
        check_missions(data["d-missions"], data["d-events"], art_frame_counts())
        check_money(data["d-money"], known)
    if errors:
        print("데이터 검사 실패:")
        print("\n".join(" - " + e for e in errors))
        return 1
    s = APP.read_text(encoding="utf-8")
    new = s
    for id_ in FILES:
        if f'id="{id_}"' not in new:
            new = new.replace('<!-- DATA:END -->', block(id_, data[id_]) + '\n<!-- DATA:END -->', 1)
            continue
        new = re.sub(rf'<script type="application/json" id="{id_}">.*?</script>', lambda _m, i=id_: block(i, data[i]), new, count=1, flags=re.S)
    if new != s:
        if embed:
            APP.write_text(new, encoding="utf-8")
            print("데이터 검사 통과 · index.html 데이터 블록을 갱신했어요.")
        else:
            print("데이터 검사는 통과했지만 index.html 안의 데이터가 data/*.json 과 달라요.")
            print("  → python3 scripts/check_data.py --embed 를 실행한 뒤 함께 커밋하세요.")
            return 1
    else:
        print("데이터 검사 통과 · index.html 과 일치해요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
