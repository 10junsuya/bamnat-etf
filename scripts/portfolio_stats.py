"""포트폴리오용 예상 적중 기록 요약 (data/track.json → 마크다운)

python3 scripts/portfolio_stats.py > 적중률.md

- live: 그날 아침 실제로 미리 낸 예상 (진짜 성적)
- back: 지난 날짜를 같은 방법으로 다시 계산해 본 것 (방법 검증용)
- 오차 = 예상 등락률 - 실제 등락률 (%p). 숫자는 모두 계산값.
"""
import json
import statistics as st
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KST = timezone(timedelta(hours=9))


def load():
    d = json.loads((ROOT / "data/track.json").read_text(encoding="utf-8"))
    names = {}
    try:
        for c, n, *_ in json.loads((ROOT / "data/etfs.json").read_text(encoding="utf-8"))["etfs"]:
            names[c] = n
    except Exception:
        pass
    rows = []
    for code, recs in (d.get("etfs") or {}).items():
        for r in recs:
            if r.get("err") is None or r.get("actual_pct") is None or r.get("pred_pct") is None:
                continue
            rows.append({"code": code, "name": names.get(code, code), **r})
    return rows


def summary(rows):
    if not rows:
        return None
    ab = [abs(r["err"]) for r in rows]
    nz = [r for r in rows if abs(r["actual_pct"]) >= 0.05]
    hit = sum(1 for r in nz if (r["pred_pct"] > 0) == (r["actual_pct"] > 0))
    return {
        "n": len(rows),
        "etfs": len({r["code"] for r in rows}),
        "from": min(r["target"] for r in rows),
        "to": max(r["target"] for r in rows),
        "mae": st.mean(ab),
        "med": st.median(ab),
        "in03": sum(1 for a in ab if a <= 0.3) / len(ab) * 100,
        "in10": sum(1 for a in ab if a <= 1.0) / len(ab) * 100,
        "dir": (hit / len(nz) * 100) if nz else None,
    }


def line(s):
    if not s:
        return "아직 기록이 없어요.\n"
    out = [
        f"- 기간: {s['from']} ~ {s['to']} · ETF {s['etfs']}개 · 예상 {s['n']}건",
        f"- 평균 오차(절댓값): **{s['mae']:.2f}%p** (가운데 값 {s['med']:.2f}%p)",
        f"- 오차 0.3%p 이내: **{s['in03']:.0f}%** · 1%p 이내: {s['in10']:.0f}%",
    ]
    if s["dir"] is not None:
        out.append(f"- 오르내림 방향 맞힘: **{s['dir']:.0f}%** (실제 움직임 0.05% 미만인 날 제외)")
    return "\n".join(out) + "\n"


def main():
    rows = load()
    live = [r for r in rows if r.get("kind") == "live"]
    back = [r for r in rows if r.get("kind") != "live"]
    now = datetime.now(KST)
    wk = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    print(f"# 노몬 예상 적중 기록 ({now:%Y-%m-%d} 기준)\n")
    print("숫자는 모두 data/track.json 으로 계산한 값(계산값)이에요. 오차 = 예상 등락률 - 실제 기준가 등락률.\n")
    print("## 실제로 미리 낸 예상 (live) — 진짜 성적\n")
    print(line(summary(live)))
    print("## 최근 7일 (live)\n")
    print(line(summary([r for r in live if r["target"] > wk])))
    print("## 방법 검증 (지난 날짜 다시 계산, back)\n")
    print(line(summary(back)))
    by = {}
    cnt = {}
    for r in live:
        cnt[r["code"]] = cnt.get(r["code"], 0) + 1
    src = live if cnt and min(cnt.values()) >= 3 else rows
    for r in src:
        by.setdefault(r["code"], []).append(abs(r["err"]))
    ranked = sorted(((st.mean(v), c, len(v)) for c, v in by.items() if len(v) >= 3))
    if ranked:
        names = {r["code"]: r["name"] for r in rows}
        print("## ETF별 (3건 이상" + (", live" if src is live else ", live+back 합쳐서") + ")\n")
        print("| | ETF | 평균 오차 | 건수 |\n|---|---|---|---|")
        for m, c, n in ranked[:5]:
            print(f"| 잘 맞음 | {names.get(c, c)} ({c}) | {m:.2f}%p | {n} |")
        for m, c, n in ranked[-3:][::-1]:
            print(f"| 덜 맞음 | {names.get(c, c)} ({c}) | {m:.2f}%p | {n} |")
        print()
    print("※ 자기소개서·포트폴리오에는 live 숫자를 쓰고, back 은 '방법을 검증했다'는 근거로만 써요.")


if __name__ == "__main__":
    main()
