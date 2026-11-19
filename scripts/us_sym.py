"""기호가 들어간 미국 티커 표(BRKB → BRK-B 등)를 앱(index.html US_SYM)에서 그대로 읽어요.

앱과 스크립트가 같은 표 하나만 쓰게 하려고 만들었어요 (대표 승인 23번, 2026-11-19).
새 기호 티커는 index.html 의 US_SYM 한 곳에만 더하면 돼요.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FALLBACK = {"BRKB": "BRK-B", "MOGA": "MOG-A", "BFB": "BF-B"}


def load():
    try:
        s = (ROOT / "index.html").read_text(encoding="utf-8")
        m = re.search(r"const US_SYM = (\{.*?\});", s)
        d = json.loads(m.group(1)) if m else {}
        return {**FALLBACK, **d} if d else dict(FALLBACK)
    except (OSError, ValueError):
        return dict(FALLBACK)


US_SYM = load()
