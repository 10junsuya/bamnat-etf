/**
 * 노몬 실시간 중계 서버 (Cloudflare Workers)
 *
 * 보안 원칙 (ops/SECURITY.md)
 * - 키(FINNHUB_API_KEY, KIS_*)는 Cloudflare 비밀값으로만 들어와요. 응답·로그·주소(URL)에 절대 안 남겨요.
 * - 읽기(GET)만 받아요. 정해진 주소·정해진 질문 칸만 받고, 나머지는 거절해요.
 * - 앱이 쓰는 종목(allow.js)만 받아요. 아무 종목이나 넣어 외부 시세 사용량을 다 쓰게 하는 공격을 막아요.
 * - 한국투자증권에는 "시세 조회"만 보낼 수 있어요. 주문·잔고·계좌 요청은 코드에서 아예 막혀 있어요.
 * - 같은 질문은 잠깐 받아 둔 답을 모두에게 나눠 줘요. 이용자가 아무리 많아도 바깥 서버는 몇 초에 한 번만 불려요.
 *   (이용자 한 명 한 명의 횟수는 제한하지 않아요)
 * - 에러 내용은 바깥에 자세히 보여주지 않아요.
 *
 * GET /health                  → 서버 상태
 * GET /quote?s=NVDA,AAPL,QQQ   → 미국 시세 (최대 40개)
 * GET /fx                      → 원/달러 환율 (실시간 소스가 안 되면 일 단위 기준환율 + 표시)
 * GET /kr?c=360750,133690      → 국내 ETF 장중 가격·iNAV (한국투자증권 키가 있으면 그걸로, 없으면 FunETF 공개 화면에서)
 * GET /usday?s=RKLB,ASTS       → 미국 주식 주간거래 시세 (한국투자증권 키가 있어야 동작, 최대 40개)
 * GET /usreg?s=RKLB            → 미국 주식 정규장 시세 (한국투자증권)
 * GET /kis-check               → 한국투자증권 연결 점검 (성공 여부와 칸 이름만, 값·키는 안 보여줘요)
 * GET /fut                     → 미국 지수 선물(나스닥100·S&P500) 움직임
 */
import { US as ALLOW_US, KR as ALLOW_KR } from "./allow.js";

const CACHE_SEC = 20;
const SYM = /^[A-Z][A-Z0-9.\-]{0,9}$/;
const KRC = /^[0-9A-Z]{6}$/;
const MAX_URL = 1024;
/* 주소마다 받을 수 있는 질문 칸 */
const ROUTES = { "/": [], "/health": [], "/quote": ["s"], "/fx": [], "/kr": ["c"], "/usday": ["s"], "/usreg": ["s"], "/kis-check": [], "/fut": [] };

/* 앱 화면 주소만 브라우저에서 부를 수 있게 해요. ALLOW_ORIGINS(쉼표 목록)가 "*"면 모두 허용(공개 전 단계). */
function corsOrigin(request, env) {
  const list = String(env.ALLOW_ORIGINS || "*").split(",").map((x) => x.trim()).filter(Boolean);
  if (list.includes("*")) return "*";
  const o = request.headers.get("origin");
  return o && list.includes(o) ? o : null;
}

let SECRETS = [];
/* 혹시라도 응답에 키 값이 섞이면 지워요 (이중 안전장치) */
const redact = (text) => SECRETS.reduce((t, k) => (k && k.length >= 8 ? t.split(k).join("[숨김]") : t), text);

function json(obj, status = 200, maxAge = CACHE_SEC, origin = "*") {
  const h = {
    "content-type": "application/json; charset=utf-8",
    "cache-control": status === 200 && maxAge > 0 ? `public, max-age=${maxAge}` : "no-store",
    "x-content-type-options": "nosniff",
    "referrer-policy": "no-referrer",
    "content-security-policy": "default-src 'none'; frame-ancestors 'none'",
    "x-frame-options": "DENY",
    "strict-transport-security": "max-age=31536000; includeSubDomains",
    "x-robots-tag": "noindex",
    "access-control-allow-methods": "GET, OPTIONS",
    "access-control-max-age": "86400",
    vary: "Origin",
  };
  if (origin) h["access-control-allow-origin"] = origin;
  return new Response(redact(JSON.stringify(obj)), { status, headers: h });
}
/* 바깥에 보여 줄 에러는 짧고 정해진 말만 */
const ERR = (msg) => ({ error: msg });
const fail = () => ERR("지금 받을 수 없어요");

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
    const r = await fetch(`https://finnhub.io/api/v1/quote?symbol=${encodeURIComponent(s)}`, { headers: { "X-Finnhub-Token": env.FINNHUB_API_KEY } });
    if (!r.ok) return fail();
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
    if (!r.ok) return fail();
    const j = await r.json();
    return { usdkrw: j.rates && j.rates.KRW, source: "유럽중앙은행 기준환율", live: false, date: j.date };
  });
}

/* ---------- 한국투자증권 (KIS) ---------- */
const KIS_BASE = "https://openapi.koreainvestment.com:9443";
async function kisToken(env) {
  // 토큰은 하루 짜리예요. 한국투자증권은 "하루 1번 발급"이 원칙이라(자주 받으면 이용 제한) 23시간 동안 재사용해요.
  return cached("kis/token", 23 * 3600, async () => {
    const r = await fetch(`${KIS_BASE}/oauth2/tokenP`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ grant_type: "client_credentials", appkey: env.KIS_APP_KEY, appsecret: env.KIS_APP_SECRET }),
    });
    if (!r.ok) return ERR("토큰을 못 받았어요");
    const j = await r.json();
    return j.access_token ? { token: j.access_token } : { error: "토큰 없음" };
  });
}
/* 이 지역 서버에 이미 받아 둔 토큰이 있는지만 봐요(새로 받지 않아요) */
async function kisTokenPeek() {
  const hit = await caches.default.match(new Request("https://cache.gnomon/kis/token"));
  return !!hit;
}
const kstNow = () => { const d = new Date(Date.now() + 9 * 3600e3); return { date: d.toISOString().slice(0, 10), clock: d.toISOString().slice(11, 19), hm: d.getUTCHours() * 60 + d.getUTCMinutes(), wd: d.getUTCDay() }; };
const kNum = (x) => { const v = parseFloat(String(x ?? "").replace(/,/g, "")); return Number.isFinite(v) ? v : null; };
/* 한국투자증권에 보낼 수 있는 요청은 이 "시세 조회" 목록뿐이에요. 주문·잔고·계좌 주소는 들어 있지 않아서 보낼 수 없어요. */
const KIS_READ_ONLY = Object.freeze({
  "/uapi/etfetn/v1/quotations/inquire-price": ["FHPST02400000"],
  "/uapi/domestic-stock/v1/quotations/inquire-price": ["FHKST01010100"],
  "/uapi/overseas-price/v1/quotations/price": ["HHDFS00000300"],
});
function kisAllowed(path, trId) {
  const ok = Object.prototype.hasOwnProperty.call(KIS_READ_ONLY, path) && KIS_READ_ONLY[path].includes(trId);
  // 이중 확인: 시세 주소(/quotations/)가 아니거나 주문·계좌 관련 글자가 있으면 무조건 거절
  return ok && path.includes("/quotations/") && !/order|trading|balance|account|acnt|ccld|psbl/i.test(path + trId);
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function kisGet(env, path, trId, params) {
  if (!kisAllowed(path, trId)) { blocked("kis-not-allowed", path); return ERR("허용되지 않은 요청이에요"); }
  const t = await kisToken(env);
  if (t.error) return t;
  // 초당 호출 한도를 넘으면(EGW00201) 잠깐 쉬었다 두 번까지 다시 물어요
  for (let tryN = 0; tryN < 3; tryN++) {
    const r = await fetch(`${KIS_BASE}${path}?${new URLSearchParams(params)}`, {
      headers: { "content-type": "application/json; charset=utf-8", authorization: `Bearer ${t.token}`, appkey: env.KIS_APP_KEY, appsecret: env.KIS_APP_SECRET, tr_id: trId, custtype: "P" },
    });
    let j = null; try { j = await r.json(); } catch (_) {}
    if (j && j.msg_cd === "EGW00201") { await sleep(1100); continue; }
    if (!r.ok || !j) return fail();
    if (j.rt_cd !== "0") return ERR("한국투자증권 응답 오류");
    return j;
  }
  return ERR("잠시 뒤 다시");
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
    if (!o || !kNum(o.stck_prpr)) return ERR("값 없음");
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
    if (!o || !kNum(o.last)) return ERR("값 없음");
    return { price: kNum(o.last), prev: kNum(o.base), change_pct: kNum(o.rate), volume: kNum(o.tvol), ex: code, time: new Date().toISOString() };
  });
}
/* ---------- 야후 파이낸스 (환율·지수 선물) ---------- */
async function yahoo(sym) {
  return cached("y/" + sym, 60, async () => {
    const r = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(sym)}?range=1d&interval=5m`, { headers: { "user-agent": "Mozilla/5.0 (gnomon-live)" } });
    if (!r.ok) return fail();
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
    if (!r.ok || !r.body) return fail();
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

/* 목록 질문(s=, c=) 정리: 대문자·중복 제거·형식 확인·앱이 쓰는 종목만 */
const pick = (raw, re, allow, max) =>
  [...new Set(String(raw || "").toUpperCase().split(",").map((x) => x.trim()).filter((x) => re.test(x) && allow.has(x)))].sort().slice(0, max);
const fieldNames = (j) => (j && j.output && typeof j.output === "object" ? Object.keys(j.output).sort() : []);

async function route(path, q, env) {
  const kis = !!(env.KIS_APP_KEY && env.KIS_APP_SECRET);
  if (path === "/" || path === "/health") return [{ ok: true, name: "gnomon-live", time: new Date().toISOString() }, 200, 0];
  if (path === "/quote") {
    if (!env.FINNHUB_API_KEY) return [ERR("미국 시세 키가 아직 없어요"), 503, 0];
    const list = pick(q.get("s"), SYM, ALLOW_US, 40);
    if (!list.length) { blocked("symbol", path); return [ERR("노몬에서 쓰는 종목만 받을 수 있어요"), 400, 0]; }
    const out = {};
    await Promise.all(list.map(async (s) => { out[s] = await finnhubQuote(env, s).catch(fail); }));
    return [{ quotes: out, time: new Date().toISOString() }, 200, CACHE_SEC];
  }
  if (path === "/fx") return [await fx(env).catch(fail), 200, 60];
  if (path === "/kr") {
    const list = pick(q.get("c"), KRC, ALLOW_KR, kis ? 20 : 8);
    if (!list.length) { blocked("symbol", path); return [ERR("노몬에서 쓰는 ETF만 받을 수 있어요"), 400, 0]; }
    const out = {};
    for (const c of list) out[c] = await (kis ? kisEtf(env, c).then((v) => (v && !v.error ? v : funetfKr(c))) : funetfKr(c)).catch(fail);
    return [{ etfs: out, source: kis ? "한국투자증권" : "FunETF", time: new Date().toISOString() }, 200, 30];
  }
  if (path === "/usday" || path === "/usreg") {
    if (!kis) return [ERR("한국투자증권 키가 아직 없어요"), 503, 0];
    const list = pick(q.get("s"), SYM, ALLOW_US, 40);
    if (!list.length) return [ERR("노몬에서 쓰는 종목만 받을 수 있어요"), 400, 0];
    const out = {}, day = path === "/usday";
    // 초당 호출 한도를 넘지 않게 하나씩 차례로 물어요 (거래소 찾기는 하루 한 번만)
    for (const s of list) out[s] = await kisUs(env, s, day).catch(fail);
    return [{ quotes: out, session: day ? "주간거래" : "정규장", source: "한국투자증권", time: new Date().toISOString() }, 200, 30];
  }
  if (path === "/kis-check") {
    // 성공 여부와 응답 칸 이름만 보여줘요(값·키·계좌 정보 없음). 5분 동안 같은 답을 나눠 줘요.
    if (!kis) return [{ ok: false, error: "한국투자증권 키가 아직 없어요" }, 200, 0];
    // 점검 때문에 토큰을 새로 받지 않아요(하루 1번 원칙). 이 지역에 토큰이 없으면 점검을 건너뛰어요
    if (!(await kisTokenPeek())) return [{ ok: true, token: "이 지역 토큰 없음 (점검 생략)", fields: [] }, 200, 0];
    const v = await cached("kis/check", 300, async () => {
      const tok = await kisToken(env);
      if (tok.error) return { ok: false, token: "실패" };
      const etf = await kisGet(env, "/uapi/etfetn/v1/quotations/inquire-price", "FHPST02400000", { fid_cond_mrkt_div_code: "J", fid_input_iscd: "0183J0" });
      const us = await kisGet(env, "/uapi/overseas-price/v1/quotations/price", "HHDFS00000300", { AUTH: "", EXCD: "NAS", SYMB: "RKLB" });
      const usd = await kisGet(env, "/uapi/overseas-price/v1/quotations/price", "HHDFS00000300", { AUTH: "", EXCD: "BAQ", SYMB: "RKLB" });
      const row = (j) => ({ ok: !j.error, fields: fieldNames(j) });
      return { ok: true, token: "ok", etf: row(etf), us: row(us), us_day: row(usd), time: new Date().toISOString() };
    }).catch(fail);
    return [v, 200, 0];
  }
  if (path === "/fut") {
    const out = {};
    for (const [k, s] of [["nq", "NQ=F"], ["es", "ES=F"]]) out[k] = await yahoo(s).catch(fail);
    return [{ fut: out, source: "Yahoo Finance", time: new Date().toISOString() }, 200, 60];
  }
  return null;
}

/* 차단 기록: 무엇이 왜 막혔는지만 남겨요(IP·질문 값 같은 개인 정보는 안 남겨요). Cloudflare 로그에서 볼 수 있어요. */
function blocked(reason, path) {
  try { console.log(JSON.stringify({ gnomon: "blocked", reason, path: String(path).slice(0, 40) })); } catch (_) {}
}

export default {
  async fetch(request, env, ctx) {
    SECRETS = [env.FINNHUB_API_KEY, env.KIS_APP_KEY, env.KIS_APP_SECRET].filter(Boolean);
    const origin = corsOrigin(request, env);
    if (request.method === "OPTIONS") return json({}, 204, 0, origin);
    if (request.method !== "GET") { blocked("method", request.method); return json(ERR("읽기(GET)만 받아요"), 405, 0, origin); }
    if (request.url.length > MAX_URL) { blocked("long-url", ""); return json(ERR("주소가 너무 길어요"), 414, 0, origin); }
    const url = new URL(request.url);
    const allowed = ROUTES[url.pathname];
    if (!allowed) { blocked("path", url.pathname); return json(ERR("없는 주소예요"), 404, 0, origin); }
    for (const k of url.searchParams.keys()) if (!allowed.includes(k)) { blocked("param", url.pathname); return json(ERR("받지 않는 질문이에요"), 400, 0, origin); }
    // 긴급 정지: 사고가 나면 MAINTENANCE=1로 다시 올려서 상태 확인(/health) 말고는 모두 멈춰요 (ops/INCIDENT.md)
    if (String(env.MAINTENANCE || "0") === "1") {
      if (url.pathname === "/" || url.pathname === "/health") return json({ ok: true, name: "gnomon-live", lockdown: true, time: new Date().toISOString() }, 200, 0, origin);
      return json(ERR("점검 중이에요. 잠시 뒤 다시 열려요"), 503, 0, origin);
    }

    // 같은 질문(정리한 뒤 기준)은 모두가 같은 답을 잠깐 나눠 써요 → 바깥 서버는 몇 초에 한 번만 불려요
    const norm = [...url.searchParams.entries()].map(([k, v]) => `${k}=${String(v).toUpperCase().split(",").map((x) => x.trim()).filter(Boolean).sort().join(",")}`).sort().join("&");
    const key = new Request(`https://resp.gnomon${url.pathname}?${norm}`);
    const cache = caches.default;
    const shared = url.pathname !== "/kis-check" && url.pathname !== "/health" && url.pathname !== "/";
    if (shared) {
      const hit = await cache.match(key);
      if (hit) { const body = await hit.text(); return json(JSON.parse(body), 200, Number(hit.headers.get("x-ttl")) || CACHE_SEC, origin); }
    }
    try {
      const r = await route(url.pathname, url.searchParams, env);
      if (!r) return json(ERR("없는 주소예요"), 404, 0, origin);
      const [body, status, ttl] = r;
      if (shared && status === 200 && ttl > 0) {
        const put = cache.put(key, new Response(redact(JSON.stringify(body)), { headers: { "cache-control": `max-age=${ttl}`, "x-ttl": String(ttl) } }));
        if (ctx && ctx.waitUntil) ctx.waitUntil(put); else await put;
      }
      return json(body, status, ttl, origin);
    } catch (e) {
      return json(ERR("서버 오류"), 500, 0, origin);  // 자세한 내용은 바깥에 안 보여줘요
    }
  },
};
