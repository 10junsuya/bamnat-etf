"""Scout · 소식 감지 프로그램 (AI 아님, 10분마다 GitHub에서 실행)

ETF에 담긴 회사들의 새 소식(기사 제목·링크)과 공시를 찾아 대기 목록에 올려요 → ops/scout/newsq.json
- 회사별 기사: 야후 파이낸스 종목 RSS (비중 큰 회사는 매번, 나머지는 돌아가며)
- 공시: SEC EDGAR 최신 8-K (담긴 회사 것만)
- 시장 전체: Fox Business 시장·경제 RSS
- 매크로·시장 매체 (2026-11-16 대표 승인, 매크로 해설 보강용): CNBC 경제·마켓, 블룸버그 경제·마켓, 월스트리트저널 마켓,
  로이터(공개 RSS가 없어 구글 뉴스 검색 피드), 파이낸셜쥬스(무료 피드) — 모두 공개 RSS의 제목·링크만
Wren(회사 소식 담당 AI)이 이 목록을 읽고 공식 출처로 확인한 뒤 회사 화면을 한국어로 갱신해요.
기사 본문은 받지 않아요(제목·링크·시각·언론사만). 실패한 출처는 건너뛰고 기록만 남겨요.
"""
import datetime as dt
import hashlib
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ops" / "scout" / "newsq.json"
KST = ZoneInfo("Asia/Seoul")
UA = {"User-Agent": "Mozilla/5.0 (gnomon-scout; +github.com/10junsuya/gnomon)"}
# SEC는 '이름 + 연락 메일' 모양의 User-Agent를 요구해요. 공개 저장소라 개인 메일 대신 GitHub 자동 작업용 noreply 주소를 써요
SEC_UA = {"User-Agent": "gnomon-app 41898282+github-actions[bot]@users.noreply.github.com", "Accept-Encoding": "identity"}
KEEP_DAYS, MAX_ITEMS, MAX_MARKET, TIER1, ROTATE = 3, 800, 300, 60, 60
YAHOO_ALIAS = {"BRKB": "BRK-B", "MOGA": "MOG-A", "BFB": "BF-B"}


def get(url, headers=UA, timeout=20):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as r:
        return r.read()


def sid(url):
    return hashlib.sha1(url.encode()).hexdigest()[:12]


def iso(s):
    try:
        return parsedate_to_datetime(s).astimezone(dt.timezone.utc).isoformat(timespec="seconds")
    except Exception:  # noqa: BLE001
        return ""


def tickers():
    """ETF에 담긴 회사들, 가장 큰 비중 순 (data/holdings.json)"""
    H = json.loads((ROOT / "data" / "holdings.json").read_text(encoding="utf-8")).get("etfs", {})
    w = {}
    for e in H.values():
        for x in e.get("top", []):
            t = re.sub(r"[-.]", "", str(x.get("ticker") or ""))
            if t and re.fullmatch(r"[A-Z]{1,6}", t):
                w[t] = max(w.get(t, 0), x.get("weight") or 0)
    return [t for t, _ in sorted(w.items(), key=lambda kv: -kv[1])]


def rss_items(xml_bytes):
    root = ET.fromstring(xml_bytes)
    for it in root.iter("item"):
        yield {k: (it.findtext(k) or "").strip() for k in ("title", "link", "pubDate", "source")}


def yahoo(t):
    s = YAHOO_ALIAS.get(t, t)
    out = []
    for x in rss_items(get(f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={s}&region=US&lang=en-US")):
        if x["title"] and x["link"]:
            out.append({"t": t, "title": x["title"], "url": x["link"], "pub": iso(x["pubDate"]), "src": "Yahoo Finance", "kind": "news"})
    return out


def sec_8k(names):
    """SEC 최신 8-K 중 담긴 회사 것 (CIK → 티커)"""
    m = json.loads(get("https://www.sec.gov/files/company_tickers.json", SEC_UA))
    cik = {str(v["cik_str"]).zfill(10): re.sub(r"[-.]", "", v["ticker"]) for v in m.values()}
    want = set(names)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(get("https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&company=&dateb=&owner=include&start=0&count=100&output=atom", SEC_UA))
    out = []
    for e in root.findall("a:entry", ns):
        title = (e.findtext("a:title", "", ns) or "").strip()
        mm = re.search(r"\((\d{10})\)", title)
        t = cik.get(mm.group(1)) if mm else None
        link = e.find("a:link", ns)
        if t in want and link is not None:
            out.append({"t": t, "title": title, "url": link.get("href"), "pub": (e.findtext("a:updated", "", ns) or "")[:25],
                        "src": "SEC EDGAR", "kind": "filing"})
    return out


def fox():
    out = []
    for sec in ("markets", "economy"):
        for x in rss_items(get(f"https://moxie.foxbusiness.com/google-publisher/{sec}.xml")):
            if x["title"] and x["link"]:
                out.append({"t": "", "title": x["title"], "url": x["link"], "pub": iso(x["pubDate"]), "src": "Fox Business", "kind": "market"})
    return out


MACRO_FEEDS = [  # (이름, 주소). 실패하면 그 출처만 건너뛰고 기록해요
    ("CNBC", "https://www.cnbc.com/id/20910258/device/rss/rss.html"),          # 경제
    ("CNBC", "https://www.cnbc.com/id/20409666/device/rss/rss.html"),          # 마켓 인사이더
    ("CNBC", "https://www.cnbc.com/id/15839135/device/rss/rss.html"),          # 실적(회사 실적 반응·분석)
    ("Bloomberg", "https://www.bloomberg.com/feeds/economics/news.rss"),
    ("Bloomberg", "https://www.bloomberg.com/feeds/markets/news.rss"),
    ("WSJ", "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain"),
    ("Reuters", "https://news.google.com/rss/search?q=site:reuters.com/markets+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("FinancialJuice", "https://www.financialjuice.com/feed.ashx?xy=rss"),
]


def macro_feeds(stat):
    out = []
    for name, url in MACRO_FEEDS:
        try:
            got = [{"t": "", "title": re.sub(r"^FinancialJuice:\s*", "", x["title"]), "url": x["link"], "pub": iso(x["pubDate"]),
                    "src": (x.get("source") or name) if name == "Reuters" else name, "kind": "market"}
                   for x in rss_items(get(url)) if x["title"] and x["link"]]
            stat[name] = stat.get(name, 0) + len(got) if isinstance(stat.get(name, 0), int) else len(got)
            out += got
        except Exception as e:  # noqa: BLE001
            stat[name] = f"실패 {type(e).__name__}"
    return out


TAG = re.compile(r"<[^>]*>")
CTRL = re.compile(r"[\x00-\x1f\x7f]")


def safe(x):
    """보안: 바깥 기사 제목은 글자만 남기고(태그·제어문자 제거, 300자), 링크는 https만 받아요.
    제목 안에 'AI에게 이렇게 해라' 같은 글이 있어도 Wren은 따르지 않아요(RULES 0-1)."""
    url = str(x.get("url") or "").strip()
    if not url.startswith("https://") or any(c in url for c in '<>" '):
        return None
    t = CTRL.sub(" ", TAG.sub("", str(x.get("title") or ""))).replace("<", "").replace(">", "").strip()[:300]
    if not t:
        return None
    return {**x, "title": t, "url": url}


def main():
    old = {}
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
        except ValueError:
            old = {}
    now = dt.datetime.now(dt.timezone.utc)
    names = tickers()
    rot = int(old.get("rot", 0))
    rest = names[TIER1:]
    pick = names[:TIER1] + (rest[rot:rot + ROTATE] + rest[:max(0, rot + ROTATE - len(rest))] if rest else [])
    stat, found = {}, []

    ok = err = 0
    for t in pick:
        try:
            found += yahoo(t); ok += 1
        except Exception:  # noqa: BLE001
            err += 1
        time.sleep(0.25)
    stat["Yahoo Finance"] = f"{ok}종목 확인 · 실패 {err}"
    mstat = {}
    found += macro_feeds(mstat)
    for k, v in mstat.items():
        stat[k] = f"{v}건" if isinstance(v, int) else v
    for name, fn in (("SEC EDGAR", lambda: sec_8k(names)), ("Fox Business", fox)):
        try:
            got = fn(); found += got; stat[name] = f"{len(got)}건"
        except Exception as e:  # noqa: BLE001
            stat[name] = f"실패 {type(e).__name__}"

    cut = (now - dt.timedelta(days=KEEP_DAYS)).isoformat()
    seen = now.isoformat(timespec="seconds")
    items = {x["id"]: x for x in old.get("items", []) if (x.get("pub") or x.get("seen", "")) >= cut}
    new = 0
    for x in filter(None, map(safe, found)):
        if x["pub"] and x["pub"] < cut:
            continue
        i = sid(x["url"])
        if i in items:
            continue
        items[i] = {"id": i, **x, "seen": seen}
        new += 1
    allx = sorted(items.values(), key=lambda x: x.get("pub") or x["seen"], reverse=True)
    xs = [x for x in allx if x["kind"] != "market"][:MAX_ITEMS] + [x for x in allx if x["kind"] == "market"][:MAX_MARKET]
    out = {"updated_kst": now.astimezone(KST).strftime("%Y-%m-%d %H:%M"), "rot": (rot + ROTATE) % max(1, len(rest)),
           "how": "Scout(프로그램)이 10분마다 모은 기사 제목·링크와 공시예요. Wren이 공식 출처로 확인한 뒤 회사 화면에 한국어로 반영해요. 본문은 받지 않아요.",
           "sources": stat, "items": xs}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if new or not OUT.exists():
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"Scout: 새 소식 {new}건 · 대기 목록 {len(xs)}건 · 확인 {len(pick)}종목 / 전체 {len(names)}")
    print(" · ".join(f"{k} {v}" for k, v in stat.items()))


if __name__ == "__main__":
    main()
