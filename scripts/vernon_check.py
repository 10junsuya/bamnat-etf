"""Vernon(숫자 품질 AI)이 매번 먼저 돌리는 점검표 → 표준 출력(마크다운)

- 자료가 제때 들어왔는지(받은 시각), 수집 오류
- 구성종목 비중 합계·시세 없는 종목
- 추정 오차: 전날 공시 기준가 × 미국 종가 변화 × 환율 변화로 맞힌 값 vs 다음 날 실제 공시 기준가
- 매크로 값이 직전보다 크게 튀었는지
판단(맞다/틀리다)은 Vernon이 원 출처와 대조해서 해요. 이 스크립트는 숫자만 모아요.
"""
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from etf_list import ETFS, GROUPS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
KST = dt.timezone(dt.timedelta(hours=9))
now = dt.datetime.now(KST)
load = lambda f: json.loads((ROOT / "data" / f).read_text(encoding="utf-8"))
live, hold, macro = load("live.json"), load("holdings.json"), load("macro.json")


def age(ts):
    try:
        t = dt.datetime.strptime(ts[:16], "%Y-%m-%d %H:%M").replace(tzinfo=KST)
        return round((now - t).total_seconds() / 3600, 1)
    except (TypeError, ValueError):
        return None


def prev_us(d):
    d = dt.date.fromisoformat(d) - dt.timedelta(days=1)
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d.isoformat()  # 미국 휴장일은 앱(US_HOL)과 달리 무시 — 휴장일 직후 결과는 걸러서 봐요


def close(t, d):
    c = live.get("closes", {}).get(d, {})
    if t in c:
        return c[t]
    q = live.get("quotes", {}).get(t)
    if q and q.get("d") == d:
        return q["p"]
    return None


def fx(d):
    h = live.get("fx", {}).get("hist", {})
    ks = sorted(k for k in h if k <= d)
    return h[ks[-1]] if ks else None


print(f"# Vernon 점검표 · {now:%Y-%m-%d %H:%M} KST\n")
print("## 1. 자료 받은 시각")
for nm, d in (("시세·기준가·환율 (live.json)", live), ("구성종목 (holdings.json)", hold), ("매크로 (macro.json)", macro)):
    print(f"- {nm}: {d.get('generated_at_kst')} ({age(d.get('generated_at_kst'))}시간 전) · 수집 오류 {len(d.get('errors', []))}건")
    for e in d.get("errors", [])[:5]:
        print(f"  - {e}")

print("\n## 2. 구성종목")
quotes = live.get("quotes", {})
for code, name, g in ETFS:
    v = hold.get("etfs", {}).get(code)
    if not v:
        print(f"- {code} {name}: 구성종목 없음")
        continue
    miss = [i["ticker"] for i in v["top"] if i.get("ticker") and i["ticker"] not in quotes]
    tw = sum(i["weight"] for i in v["top"])
    flag = "" if (v["kind"] == "index" or 97 <= tw + v.get("cash_weight", 0) <= 103) else " ⚠ 비중 합계 확인"
    print(f"- {code} {name}: {v['src']} · {v['asof']} · {v['n_total']}종목 · 표시 비중 {tw:.1f}%{flag}" + (f" · 시세 없음 {miss}" if miss else ""))

print("\n## 3. 추정 오차 (예상 기준가 ÷ 실제 기준가 − 1)")
for code, name, g in ETFS:
    rows = [r for r in live.get("kr", {}).get(code, []) if r.get("nav")]
    G, v = GROUPS[g], hold.get("etfs", {}).get(code, {})
    errs = []
    for r0, r1 in zip(rows, rows[1:]):
        u0, u1, f0, f1 = prev_us(r0["d"]), prev_us(r1["d"]), fx(r0["d"]), fx(r1["d"])
        if not (f0 and f1):
            continue
        legs = [(G["proxy"], 1.0)] if G["kind"] == "index" else [(i["ticker"], i["weight"] / 100) for i in v.get("top", [])]
        f, ok = v.get("cash_weight", 0) / 100 if G["kind"] == "pdf" else 0.0, True
        for t, w in legs:
            a, b = close(t, u1), close(t, u0)
            if not (a and b):
                ok = False
                break
            f += w * a / b
        if ok:
            errs.append((r1["d"], r0["nav"] * f * f1 / f0 / r1["nav"] - 1))
    if errs:
        avg = sum(abs(e) for _, e in errs) / len(errs)
        big = [f"{d} {e*100:+.2f}%" for d, e in errs if abs(e) > 0.01]
        print(f"- {code} {name}: {len(errs)}일 · 평균 ±{avg*100:.2f}%" + (f" · 1% 넘음: {big}" if big else ""))
    else:
        print(f"- {code} {name}: 아직 계산할 기록이 없어요 (기준가 {len(rows)}일)")

print("\n## 4. 매크로")
for k, v in macro.get("ind", {}).items():
    s = [x for _, x in v.get("series", [])]
    jump = ""
    if len(s) >= 3:
        d = [abs(b - a) for a, b in zip(s[:-1], s[1:])][:-1]
        avgd = sum(d) / len(d) if d else 0
        if avgd and abs(s[-1] - s[-2]) > 4 * avgd:
            jump = f" ⚠ 직전보다 크게 바뀜 ({s[-2]} → {s[-1]})"
    val = v.get("a", v.get("now"))
    print(f"- {k}: {val} · 기준 {v.get('asof')} · {v.get('src')}{jump}" + (f" · {v['note']}" if v.get("note") else ""))
