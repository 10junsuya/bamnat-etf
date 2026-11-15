"""Argus — 노몬 경비 프로그램 (AI 아님, GitHub에서 10분마다)

보는 것
1. 실시간 서버(gnomon-live)가 살아 있는지
2. 자동 수집 자료가 너무 오래되지 않았는지 (평일 기준)
3. 미국장이 열려 있을 때: 같은 지수 미국 ETF(SPY·QQQ·SOXQ·SMH·SCHD)와 watchlist 종목이 크게 움직였는지
4. 앱 데이터 검사(check_data.py)가 통과하는지
새 알림만 ops/board/argus.md 에 적고(같은 알림은 6시간에 한 번), 상태는 ops/argus/state.json 에 남겨요.
앱 숫자가 틀릴 수 있는 '긴급'이면 실행을 실패로 끝내서 GitHub 알림 메일이 가게 해요.
"""
import datetime as dt, json, subprocess, sys, urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
KST, NY = ZoneInfo("Asia/Seoul"), ZoneInfo("America/New_York")
LIVE = "https://gnomon-live.leejoonsoo85.workers.dev"
STATE, BOARD = ROOT / "ops/argus/state.json", ROOT / "ops/board/argus.md"
now = dt.datetime.now(KST)
sys.path.insert(0, str(ROOT / "scripts"))
from etf_list import GROUPS  # noqa: E402


def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "gnomon-argus"}), timeout=20) as r:
        return json.loads(r.read().decode())


def age_h(ts):
    try:
        return (now - dt.datetime.strptime(ts[:16], "%Y-%m-%d %H:%M").replace(tzinfo=KST)).total_seconds() / 3600
    except (TypeError, ValueError):
        return 999


alerts = []  # (key, 급함 여부, 제목, 내용)
# 1. 서버
try:
    h = get(LIVE + "/health")
    if not h.get("ok", True):
        alerts.append(("server", True, "실시간 서버 이상", json.dumps(h, ensure_ascii=False)[:200]))
except Exception as e:  # noqa: BLE001
    alerts.append(("server", True, "실시간 서버 응답 없음", f"{type(e).__name__}: {str(e)[:120]}"))

# 2. 자료 나이 (평일만, 넉넉하게)
if now.weekday() < 5:
    for f, lim in (("live.json", 30), ("holdings.json", 54), ("macro.json", 30)):
        try:
            a = age_h(json.loads((ROOT / "data" / f).read_text(encoding="utf-8")).get("generated_at_kst"))
        except (OSError, ValueError):
            a = 999
        if a > lim:
            alerts.append((f"stale:{f}", f == "live.json", f"자동 수집이 멈춘 듯해요: {f}", f"마지막으로 받은 지 {a:.0f}시간 (기준 {lim}시간)"))

# 3. 큰 움직임 (미국 정규장 + 장 마감 후 2시간)
ny = dt.datetime.now(NY)
wl = json.loads((ROOT / "ops/watchlist.json").read_text(encoding="utf-8"))
if ny.weekday() < 5 and (9 * 60 + 30) <= ny.hour * 60 + ny.minute <= 18 * 60:
    proxies = sorted({g["proxy"] for g in GROUPS.values() if g.get("proxy")})
    items = [i for i in wl.get("items", []) if i.get("until", "9999") >= now.strftime("%Y-%m-%d")]
    syms = proxies + [i["t"] for i in items if i["t"] not in proxies]
    try:
        q = get(LIVE + "/quote?s=" + ",".join(syms[:40]))
        q = q.get("quotes", q)
        for t in syms:
            v = q.get(t) or {}
            dp = v.get("change_pct")
            if dp is None:
                continue
            lim = next((i["move"] for i in items if i["t"] == t), None) or (wl["default"]["proxy_move"] if t in proxies else wl["default"]["stock_move"])
            if abs(dp) >= lim:
                why = next((i["why"] for i in items if i["t"] == t), "같은 지수 미국 ETF")
                alerts.append((f"move:{t}:{ny:%Y-%m-%d}", False, f"{t} {dp:+.1f}% (기준 ±{lim}%)", f"{why} · 가격 {v.get('price')} · {v.get('time')}"))
    except Exception as e:  # noqa: BLE001
        alerts.append(("quote", False, "시세를 못 받았어요", f"{type(e).__name__}: {str(e)[:120]}"))

# 4. 앱 데이터 검사
r = subprocess.run([sys.executable, str(ROOT / "scripts/check_data.py")], capture_output=True, text=True)
if r.returncode != 0:
    alerts.append(("check_data", True, "앱 데이터 검사 실패", (r.stdout + r.stderr).strip()[-400:]))

# 새 알림만 기록
state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"seen": {}}
seen, new = state.get("seen", {}), []
for key, urgent, title, body in alerts:
    last = seen.get(key)
    if last and age_h(last) < 6:
        continue
    seen[key] = now.strftime("%Y-%m-%d %H:%M")
    new.append((key, urgent, title, body))
state = {"last_run_kst": now.strftime("%Y-%m-%d %H:%M"), "alerts_now": [a[2] for a in alerts],
         "seen": {k: v for k, v in seen.items() if age_h(v) < 72}}
STATE.parent.mkdir(parents=True, exist_ok=True)
if new:
    with BOARD.open("a", encoding="utf-8") as f:
        for i, (key, urgent, title, body) in enumerate(new, 1):
            f.write(f"\n### G-{now:%Y%m%d-%H%M}-{i} · {'알림(긴급)' if urgent else '알림'} · {title}\n- 시각: {now:%Y-%m-%d %H:%M} KST\n- 내용: {body}\n- 요청: {'Conrad 확인 바람 (긴급)' if urgent else 'Vernon 참고'}\n")
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"Argus {now:%H:%M}: 지금 알림 {len(alerts)}건 · 새로 적음 {len(new)}건")
for a in alerts:
    print(" -", ("[긴급] " if a[1] else "") + a[2])
sys.exit(2 if any(a[1] for a in new) else 0)
