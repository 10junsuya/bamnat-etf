"""data/companies.json을 원래 모양(회사 한 줄씩)으로 저장해요. 다른 스크립트에서 import 해서 써요."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMP, MONEY = ROOT / "data" / "companies.json", ROOT / "data" / "money.json"


def load():
    return json.loads(COMP.read_text(encoding="utf-8")), json.loads(MONEY.read_text(encoding="utf-8"))


def save(c, m=None):
    out = ["{"]
    keys = list(c.keys())
    for i, k in enumerate(keys):
        v = c[k]
        end = "," if i < len(keys) - 1 else ""
        if isinstance(v, dict) and v and k != "about":
            out.append(f' {json.dumps(k, ensure_ascii=False)}: {{')
            items = list(v.items())
            for j, (t, x) in enumerate(items):
                out.append(f'  {json.dumps(t, ensure_ascii=False)}: {json.dumps(x, ensure_ascii=False)}' + ("," if j < len(items) - 1 else ""))
            out.append(" }" + end)
        else:
            out.append(f' {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}' + end)
    out.append("}")
    COMP.write_text("\n".join(out) + "\n", encoding="utf-8")
    if m is not None:
        MONEY.write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
