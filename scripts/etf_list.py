"""앱에 넣는 ETF 목록: data/etfs.json 이 원본이에요(앱도 같은 파일을 씀).
kind: index = 같은 지수를 따르는 미국 ETF(proxy) 가격으로 밤사이 변화를 계산 / pdf = 담긴 회사 비중 × 각 회사 가격으로 계산"""
import json
from pathlib import Path

_D = json.loads((Path(__file__).resolve().parent.parent / "data" / "etfs.json").read_text(encoding="utf-8"))
GROUPS = _D["groups"]
ETFS = [tuple(x) for x in _D["etfs"]]


def isin(code):
    s = "KR7" + code + "00"
    digits = "".join(str(int(c, 36)) for c in s)
    tot = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch) * (2 if i % 2 == 0 else 1)
        tot += d // 10 + d % 10
    return s + str((10 - tot % 10) % 10)
