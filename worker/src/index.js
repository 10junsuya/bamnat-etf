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
 * GET /kr?c=360750,133690      → 국내 ETF 장중 가격·iNAV (한국투자증권 키가 들어오면 동작)
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
  // 2) 유럽중앙은행 기준환율 (하루 한 번)
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
async function kisEtf(env, code) {
  return cached("kr/" + code, CACHE_SEC, async () => {
    const t = await kisToken(env);
    if (t.error) return t;
    const u = `${KIS_BASE}/uapi/domestic-stock/v1/quotations/inquire-price?FID_COND_MRKT_DIV_CODE=J&FID_INPUT_ISCD=${code}`;
    const r = await fetch(u, {
      headers: { authorization: `Bearer ${t.token}`, appkey: env.KIS_APP_KEY, appsecret: env.KIS_APP_SECRET, tr_id: "FHKST01010100", custtype: "P" },
    });
    if (!r.ok) return { error: `HTTP ${r.status}` };
    const j = await r.json();
    const o = j.output || {};
    if (j.rt_cd !== "0" || !o.stck_prpr) return { error: j.msg1 || "값 없음" };
    return { price: +o.stck_prpr, change_pct: +o.prdy_ctrt, nav: o.nav ? +o.nav : null, time: new Date().toISOString() };
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
        if (!(env.KIS_APP_KEY && env.KIS_APP_SECRET)) return json({ error: "한국투자증권 키가 아직 없어요" }, 503, 0);
        const list = [...new Set((url.searchParams.get("c") || "").toUpperCase().split(",").map((x) => x.trim()).filter((x) => KRC.test(x)))].slice(0, 20);
        if (!list.length) return json({ error: "종목코드를 c=360750 처럼 적어 주세요" }, 400, 0);
        const out = {};
        for (const c of list) out[c] = await kisEtf(env, c).catch((e) => ({ error: String(e).slice(0, 80) }));
        return json({ etfs: out, time: new Date().toISOString() });
      }
      return json({ error: "없는 주소예요" }, 404, 0);
    } catch (e) {
      return json({ error: "서버 오류", detail: String(e).slice(0, 120) }, 500, 0);
    }
  },
};
