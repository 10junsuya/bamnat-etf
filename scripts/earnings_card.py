"""실적 카드(data/earnings.json) 한 곳을 새로 쓰는 도우미.

사용 예 (금액은 모두 백만 단위):
    from scripts.earnings_card import card, save
    card("NVDA", p="3분기 · 2026년 8~10월", tag="+60%",
         rows=[["매출", "..."], ["데이터센터", "..."]],
         note="무엇이 이끌었는지 1~2문장. 계산한 값이 있으면 여기 밝혀요.",
         src=[["회사 발표", "https://..."], ["예상치(출처)", "https://..."]],
         cur="usd", prev=35082, lab="8~10월", now=57006, est=54900,
         next_label="11~1월", guide=[63700, 66300], cons=None, asof=None,
         when="2027년 2월 말 (예상)", gtext=None, metric=None)
    save()
그다음 `python3 scripts/check_data.py --embed` 로 앱에 넣어요.
"""
import json
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "data" / "earnings.json"
Q = json.loads(PATH.read_text(encoding="utf-8"))


def card(t, p, tag, rows, note, src, cur, prev, lab, now, est, next_label,
         guide=None, cons=None, asof=None, when="", gtext=None, metric=None):
    ch = {"cur": cur, "now": [lab, now], "est": est,
          "next": {"label": next_label, "guide": guide, "cons": cons, "when": when}}
    if prev is not None:
        ch["prev"] = ["1년 전", prev]
    if asof:
        ch["next"]["asof"] = asof
    if gtext:
        ch["next"]["gtext"] = gtext
    if metric:
        ch["metric"] = metric
    Q[t] = {"p": p, "tag": tag, "rows": rows, "note": note, "src": src, "chart": ch}


def save():
    PATH.write_text(json.dumps(Q, ensure_ascii=False, indent=1), encoding="utf-8")
