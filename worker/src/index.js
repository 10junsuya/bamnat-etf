/**
 * 노몬 실시간 중계 서버 (Cloudflare Workers)
 *
 * - 키(FINNHUB_API_KEY, KIS_*)는 Cloudflare 비밀값으로만 들어와요. 응답·로그에 절대 안 남겨요.
 * - 같은 종목은 20초 동안 받아 둔 값을 재사용해요(무료 사용량 보호, 사용자가 많아도 버팀).
 * - 읽기(GET)만 받아요.
 *
 * GET /health                  → 서버 상태와 어떤 키가 들어 있는지(값은 안 보여줌)
 * GET /quote?s=NVDA,AAPL,QQQ   → 미국 시세 (최대 40개)
 * GET /fx                      → 원/달러 환율 (실시간 소스가 안 되면 일 단위 기준환율 + 표시)
 * GET /kr?c=360750,133690      → 국내 ETF 장중 가격·iNAV (한국투자증권 키가 있으면 그걸로, 없으면 FunETF 공개 화면에서, 최대 8개)
 * GET /usday?s=RKLB,ASTS        → 미국 주식 주간거래 시세 (한국 낮 시간, 한국투자증권 키가 있어야 동작, 최대 40개)
 * GET /kis-check               → 한국투자증권 연결 점검 (키 값은 안 보여줘요)
 * GET /fut                     → 미국 지수 선물(나스닥100·S&P500) 지난 정산가 대비 움직임 (미국 장이 닫혀 있을 때 참고)
 */
const CACHE_SEC = 20;
const SYM = /^[A-Z][A-Z0-9.\-]{0,9}$/;
const KRC = /^[0-9A-Z]{6}$/;

const json = (obj, status = 200, maxAge = CACHE_SEC) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "access-control-allow-origin": "*",
      "access-control-allow-methods": "GET, OPTIONS",
      "cache-control": `public, max-age=${maxAge}`,
    },
  });

async function cached(key, ttl, fn) {
  const cache = caches.default;
  const req = new Request("https://cache.gnomon/" + key);
  const hit = await cache.match(req);
  if (hit) return hit.json();
  const val = await fn();
  if (val && !val.error) await cache.put(req, new Response(JSON.stringify(val), { headers: { "cache-control": `max-age=${ttl}` } }));
  return val;
}

async function finnhubQuote(env, s) {
  return cached("q/" + s, CACHE_SEC, async () => {
    const r = await fetch(`https://finnhub.io/api/v1/quote?symbol=${encodeURIComponent(s)}&token=${env.FINNHUB_API_KEY}`);
    if (!r.ok) return { error: `HTTP ${r.status}` };
    const q = await r.json();
    if (!q || typeof q.c !== "number" || q.c === 0) return { error: "값 없음" };
    return { price: q.c, prev: q.pc, change_pct: q.dp, time: q.t ? new Date(q.t * 1000).toISOString() : null };
  });
}

async function fx(env) {
  // 1) Finnhub 외환 시세 (무료 플랜에서 안 될 수 있어요)
  if (env.FINNHUB_API_KEY) {
    const v = await finnhubQuote(env, "OANDA:USD_KRW").catch(() => null);
    if (v && !v.error) return { usdkrw: v.price, source: "Finnhub (OANDA)", live: true, time: v.time };
  }
  // 2) 야후 파이낸스 원/달러 (몇 분 늦을 수 있어요)
  const y = await yahoo("KRW=X").catch(() => null);
  if (y && !y.error && y.price > 500) return { usdkrw: y.price, source: "Yahoo Finance", live: true, time: y.time };
  // 3) 유럽중앙은행 기준환율 (하루 한 번)
  return cached("fx/ecb", 3600, async () => {
    const r = await fetch("https://api.frankfurter.dev/v1/latest?base=USD&symbols=KRW");
    if (!r.ok) return { error: `HTTP ${r.status}` };
    const j = await r.json();
    return { usdkrw: j.rates && j.rates.KRW, source: "유럽중앙은행 기준환율", live: false, date: j.date };
  });
}

/* ---------- 한국투자증권 (KIS) ---------- */
const KIS_BASE = "https://openapi.koreainvestment.com:9443";
async function kisToken(env) {
  // 토큰은 하루 짜리라 6시간 동안 재사용해요.
  return cached("kis/token", 6 * 3600, async () => {
    const r = await fetch(`${KIS_BASE}/oauth2/tokenP`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ grant_type: "client_credentials", appkey: env.KIS_APP_KEY, appsecret: env.KIS_APP_SECRET }),
    });
    if (!r.ok) return { error: `토큰 HTTP ${r.status}` };
    const j = await r.json();
    return j.access_token ? { token: j.access_token } : { error: "토큰 없음" };
  });
}
const kstNow = () => { const d = new Date(Date.now() + 9 * 3600e3); return { date: d.toISOString().slice(0, 10), clock: d.toISOString().slice(11, 19), hm: d.getUTCHours() * 60 + d.getUTCMinutes(), wd: d.getUTCDay() }; };
const kNum = (x) => { const v = parseFloat(String(x ?? "").replace(/,/g, "")); return Number.isFinite(v) ? v : null; };
async function kisGet(env, path, trId, params) {
  const t = await kisToken(env);
  if (t.error) return t;
  const r = await fetch(`${KIS_BASE}${path}?${new URLSearchParams(params)}`, {
    headers: { "content-type": "application/json; charset=utf-8", authorization: `Bearer ${t.token}`, appkey: env.KIS_APP_KEY, appsecret: env.KIS_APP_SECRET, tr_id: trId, custtype: "P" },
  });
  if (!r.ok) return { error: `HTTP ${r.status}` };
  const j = await r.json();
  if (j.rt_cd !== "0") return { error: j.msg1 || j.msg_cd || "실패" };
  return j;
}
/* 국내 ETF: ETF 전용 현재가(가격·NAV) → 안 되면 일반 현재가 + FunETF iNAV */
async function kisEtf(env, code) {
  return cached("kr/" + code, CACHE_SEC, async () => {
    const k = kstNow();
    const state = k.wd === 0 || k.wd === 6 ? "휴장" : k.hm < 9 * 60 ? "장전" : k.hm < 15 * 60 + 30 ? "장중" : "장마감";
    let j = await kisGet(env, "/uapi/etfetn/v1/quotations/inquire-price", "FHPST02400000", { fid_cond_mrkt_div_code: "J", fid_input_iscd: code });
    let o = j && j.output;
    if (!o || !kNum(o.stck_prpr)) {
      j = await kisGet(env, "/uapi/domestic-stock/v1/quotations/inquire-price", "FHKST01010100", { FID_COND_MRKT_DIV_CODE: "J", FID_INPUT_ISCD: code });
      o = j && j.output;
    }
    if (!o || !kNum(o.stck_prpr)) return { error: (j && j.error) || "값 없음" };
    const price = kNum(o.stck_prpr), chg = kNum(o.prdy_vrss) ?? 0;
    let inav = kNum(o.nav), navChg = kNum(o.nav_prdy_vrss), prevNav = kNum(o.prdy_clpr_nav) ?? (inav != null && navChg != null ? inav - navChg : null);
    let navPct = kNum(o.nav_prdy_ctrt) ?? (inav && prevNav ? (inav / prevNav - 1) * 100 : null);
    let src = "한국투자증권";
    if (inav == null) { const f = await funetfKr(code).catch(() => null); if (f && !f.error) { inav = f.inav; navPct = f.inav_change_pct; prevNav = f.prev_nav; src = "한국투자증권 · iNAV FunETF"; } }
    return { price, change: chg, change_pct: kNum(o.prdy_ctrt) ?? 0, prev_close: price - chg, inav, inav_change_pct: navPct, prev_nav: prevNav,
      date: k.date, clock: k.clock, state, source: src, time: new Date().toISOString() };
  });
}
/* 미국 주식 (한국투자증권): 거래소 찾기 → 정규장 시세, 한국 낮 시간엔 주간거래(블루오션) 시세 */
const US_EX = ["NAS", "NYS", "AMS"], DAY_EX = { NAS: "BAQ", NYS: "BAY", AMS: "BAA" };
async function kisUs(env, sym, day) {
  const exKey = "kx/" + sym;
  let ex = await cached(exKey, 86400, async () => {
    for (const e of US_EX) { const j = await kisGet(env, "/uapi/overseas-price/v1/quotations/price", "HHDFS00000300", { AUTH: "", EXCD: e, SYMB: sym }); if (j && j.output && kNum(j.output.last)) return { ex: e }; }
    return { error: "거래소를 못 찾았어요" };
  });
  if (ex.error) return ex;
  const code = day ? DAY_EX[ex.ex] : ex.ex;
  return cached(`ku/${code}/${sym}`, CACHE_SEC, async () => {
    const j = await kisGet(env, "/uapi/overseas-price/v1/quotations/price", "HHDFS00000300", { AUTH: "", EXCD: code, SYMB: sym });
    const o = j && j.output;
    if (!o || !kNum(o.last)) return { error: (j && j.error) || "값 없음" };
    return { price: kNum(o.last), prev: kNum(o.base), change_pct: kNum(o.rate), volume: kNum(o.tvol), ex: code, time: new Date().toISOString() };
  });
}
/* ---------- 야후 파이낸스 (환율·지수 선물) ---------- */
async function yahoo(sym) {
  return cached("y/" + sym, 60, async () => {
    const r = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(sym)}?range=1d&interval=5m`, { headers: { "user-agent": "Mozilla/5.0 (gnomon-live)" } });
    if (!r.ok) return { error: `HTTP ${r.status}` };
    const j = await r.json();
    const m = j && j.chart && j.chart.result && j.chart.result[0] && j.chart.result[0].meta;
    if (!m || typeof m.regularMarketPrice !== "number") return { error: "값 없음" };
    return { price: m.regularMarketPrice, prev: m.chartPreviousClose ?? m.previousClose ?? null, time: m.regularMarketTime ? new Date(m.regularMarketTime * 1000).toISOString() : null };
  });
}

/* ---------- FunETF 공개 화면 (국내 ETF 현재가·iNAV) ---------- */
function krIsin(code) {
  const s = "KR7" + code + "00";
  const digits = [...s].map((c) => parseInt(c, 36).toString()).join("");
  let tot = 0;
  [...digits].reverse().forEach((ch, i) => { const d = Number(ch) * (i % 2 === 0 ? 2 : 1); tot += Math.floor(d / 10) + (d % 10); });
  return s + ((10 - (tot % 10)) % 10);
}
const numOf = (x) => { const v = parseFloat(String(x).replace(/,/g, "")); return Number.isFinite(v) ? v : null; };
async function funetfKr(code) {
  return cached("kf/" + code, 30, async () => {
    const r = await fetch(`https://www.funetf.co.kr/product/etf/view/${krIsin(code)}`, { headers: { "user-agent": "Mozilla/5.0 (gnomon-live)" } });
    if (!r.ok || !r.body) return { error: `HTTP ${r.status}` };
    // 페이지가 커서, 필요한 윗부분(현재가·iNAV)까지만 읽고 멈춰요
    const reader = r.body.getReader(), dec = new TextDecoder();
    let html = "", stopAt = -1;
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      html += dec.decode(value, { stream: true });
      if (stopAt < 0) { const i = html.indexOf('id="goNav"'); if (i >= 0) stopAt = i + 4000; }
      if (stopAt > 0 && html.length > stopAt) { reader.cancel().catch(() => {}); break; }
      if (html.length > 1500000) { reader.cancel().catch(() => {}); break; }
    }
    const t = html.replace(/\s+/g, " ");
    const block = (from) => {
      const i = t.indexOf(from); if (i < 0) return null;
      const m = t.slice(i).match(/<p class="top"><span>\s*([\d,.]+)\s*<\/span>원<\/p>\s*<p class="bottom">\s*<span class="(minus|plus|zero|)[^"]*">\s*([\d,.]+)?\s*\(\s*([\d.]+)%\s*\)/);
      if (!m) return null;
      const sign = m[2] === "minus" ? -1 : m[2] === "plus" ? 1 : 0;
      return { v: numOf(m[1]), chg: sign * (numOf(m[3]) || 0), pct: sign * (numOf(m[4]) || 0) };
    };
    const tm = (t.match(/prd-info-top-summary-time">\s*(\d{2})\.(\d{2})\.(\d{2})\s+(\d{2}:\d{2}:\d{2})\s*\(([^)]*)\)/) || []);
    const p = block("현재가"), n = block('id="goNav"');
    if (!p || !p.v) return { error: "현재가를 못 찾았어요" };
    return {
      price: p.v, change: p.chg, change_pct: p.pct, prev_close: p.v - p.chg,
      inav: n ? n.v : null, inav_change_pct: n ? n.pct : null, prev_nav: n && n.v ? Math.round((n.v - n.chg) * 100) / 100 : null,
      date: tm[1] ? `20${tm[1]}-${tm[2]}-${tm[3]}` : null, clock: tm[4] || null, state: tm[5] || null,
      source: "FunETF", time: new Date().toISOString(),
    };
  });
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") return json({}, 204, 0);
    if (request.method !== "GET") return json({ error: "GET만 받아요" }, 405, 0);
    const url = new URL(request.url);
    try {
      if (url.pathname === "/" || url.pathname === "/health") {
        return json({ ok: true, name: "gnomon-live", keys: { finnhub: !!env.FINNHUB_API_KEY, kis: !!(env.KIS_APP_KEY && env.KIS_APP_SECRET) }, time: new Date().toISOString() }, 200, 0);
      }
      if (url.pathname === "/quote") {
        if (!env.FINNHUB_API_KEY) return json({ error: "미국 시세 키가 아직 없어요" }, 503, 0);
        const list = [...new Set((url.searchParams.get("s") || "").toUpperCase().split(",").map((x) => x.trim()).filter((x) => SYM.test(x)))].slice(0, 40);
        if (!list.length) return json({ error: "종목을 s=NVDA,AAPL 처럼 적어 주세요" }, 400, 0);
        const out = {};
        await Promise.all(list.map(async (s) => { out[s] = await finnhubQuote(env, s).catch((e) => ({ error: String(e).slice(0, 80) })); }));
        return json({ quotes: out, time: new Date().toISOString() });
      }
      if (url.pathname === "/fx") return json(await fx(env), 200, 60);
      if (url.pathname === "/kr") {
        const kis = !!(env.KIS_APP_KEY && env.KIS_APP_SECRET);
        const list = [...new Set((url.searchParams.get("c") || "").toUpperCase().split(",").map((x) => x.trim()).filter((x) => KRC.test(x)))].slice(0, kis ? 20 : 8);
        if (!list.length) return json({ error: "종목코드를 c=360750 처럼 적어 주세요" }, 400, 0);
        const out = {};
        for (const c of list) out[c] = await (kis ? kisEtf(env, c).then((v) => (v && !v.error ? v : funetfKr(c))) : funetfKr(c)).catch((e) => ({ error: String(e).slice(0, 80) }));
        return json({ etfs: out, source: kis ? "한국투자증권" : "FunETF", time: new Date().toISOString() }, 200, 30);
      }
      if (url.pathname === "/usday" || url.pathname === "/usreg") {
        if (!(env.KIS_APP_KEY && env.KIS_APP_SECRET)) return json({ error: "한국투자증권 키가 아직 없어요" }, 503, 0);
        const list = [...new Set((url.searchParams.get("s") || "").toUpperCase().split(",").map((x) => x.trim()).filter((x) => SYM.test(x)))].slice(0, 40);
        if (!list.length) return json({ error: "종목을 s=RKLB,ASTS 처럼 적어 주세요" }, 400, 0);
        const out = {}, day = url.pathname === "/usday";
        for (let i = 0; i < list.length; i += 5) {  // 초당 호출 한도를 넘지 않게 5개씩
          await Promise.all(list.slice(i, i + 5).map(async (s) => { out[s] = await kisUs(env, s, day).catch((e) => ({ error: String(e).slice(0, 80) })); }));
        }
        return json({ quotes: out, session: day ? "주간거래" : "정규장", source: "한국투자증권", time: new Date().toISOString() }, 200, 30);
      }
      if (url.pathname === "/kis-check") {
        if (!(env.KIS_APP_KEY && env.KIS_APP_SECRET)) return json({ ok: false, error: "한국투자증권 키가 아직 없어요" }, 200, 0);
        const tok = await kisToken(env);
        const etf = tok.error ? tok : await kisGet(env, "/uapi/etfetn/v1/quotations/inquire-price", "FHPST02400000", { fid_cond_mrkt_div_code: "J", fid_input_iscd: "0183J0" });
        const us = tok.error ? tok : await kisGet(env, "/uapi/overseas-price/v1/quotations/price", "HHDFS00000300", { AUTH: "", EXCD: "NAS", SYMB: "RKLB" });
        const usd = tok.error ? tok : await kisGet(env, "/uapi/overseas-price/v1/quotations/price", "HHDFS00000300", { AUTH: "", EXCD: "BAQ", SYMB: "RKLB" });
        const pick = (j) => (j && j.output ? j.output : j);
        return json({ ok: !tok.error, token: tok.error || "ok", etf: pick(etf), us: pick(us), us_day: pick(usd) }, 200, 0);
      }
      if (url.pathname === "/fut") {
        const out = {};
        for (const [k, s] of [["nq", "NQ=F"], ["es", "ES=F"]]) out[k] = await yahoo(s).catch((e) => ({ error: String(e).slice(0, 80) }));
        return json({ fut: out, source: "Yahoo Finance", time: new Date().toISOString() }, 200, 60);
      }
      return json({ error: "없는 주소예요" }, 404, 0);
    } catch (e) {
      return json({ error: "서버 오류", detail: String(e).slice(0, 120) }, 500, 0);
    }
  },
};
