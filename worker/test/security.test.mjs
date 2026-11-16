// 실시간 서버 보안 시험: 서버를 올리기 전에 매번 돌려요. 하나라도 실패하면 올리지 않아요.
const store = new Map();
globalThis.caches = { default: {
  async match(req){ const v = store.get(req.url); return v ? new Response(v.body, {headers: v.headers}) : undefined; },
  async put(req, res){ store.set(req.url, {body: await res.text(), headers: Object.fromEntries(res.headers)}); } } };
const calls = [];
const KEY = "FINNHUBSECRETKEY123456";
globalThis.fetch = async (url, opt={}) => {
  calls.push({url: String(url), headers: opt.headers||{}});
  if (String(url).includes("finnhub")) return new Response(JSON.stringify({c: 100, pc: 99, dp: 1.01, t: 1700000000, leak: "key=" + KEY}), {status:200});
  if (String(url).includes("koreainvestment")) return new Response(JSON.stringify({rt_cd:"0", output:{last:"5", base:"4", rate:"1"}, access_token:"TOK"}));
  return new Response("{}", {status: 500});
};
const { default: w } = await import(new URL("../src/index.js", import.meta.url));
const env = { FINNHUB_API_KEY: KEY, KIS_APP_KEY: "KISAPPKEY000111", KIS_APP_SECRET: "KISSECRET999888", ALLOW_ORIGINS: "https://good.app" };
const go = async (path, init={}) => { const r = await w.fetch(new Request("https://x.dev" + path, init), env, {waitUntil(){}}); return [r.status, r.headers, await r.text()]; };
let bad = 0;
const ok = (name, cond) => { if (!cond) bad++; console.log((cond ? "통과" : "실패!!") + "  " + name); };

let [st, h, b] = await go("/quote", {method: "POST"}); ok("POST 거절 (405)", st === 405);
[st] = await go("/admin"); ok("없는 주소 (404)", st === 404);
[st] = await go("/quote?s=NVDA&x=1"); ok("모르는 질문 칸 거절 (400)", st === 400);
[st] = await go("/quote?s=" + "A,".repeat(600)); ok("너무 긴 주소 (414)", st === 414);
[st, h, b] = await go("/quote?s=ZZZZZ,QWERT"); ok("앱에 없는 종목만 → 거절 (400)", st === 400);
calls.length = 0;
[st, h, b] = await go("/quote?s=NVDA,ZZZZZ,AAPL");
const j = JSON.parse(b);
ok("앱 종목만 받아 줌 (NVDA,AAPL만)", Object.keys(j.quotes).join() === "AAPL,NVDA");
ok("키가 주소(URL)에 안 들어감", calls.every(c => !c.url.includes(KEY)));
ok("키가 응답에 안 섞임", !b.includes(KEY));
ok("모르는 사이트(Origin 없음)엔 CORS 허용 안 함", !h.get("access-control-allow-origin"));
[st, h] = await go("/quote?s=NVDA", {headers: {origin: "https://evil.site"}}); ok("다른 사이트 브라우저 차단", !h.get("access-control-allow-origin"));
[st, h] = await go("/quote?s=NVDA", {headers: {origin: "https://good.app"}}); ok("우리 앱 주소는 허용", h.get("access-control-allow-origin") === "https://good.app");
ok("보안 헤더", h.get("x-content-type-options") === "nosniff" && h.get("content-security-policy").includes("default-src 'none'"));
calls.length = 0;
for (let i = 0; i < 50; i++) await go("/quote?s=AAPL,NVDA");
await go("/quote?s=nvda,aapl");
ok("같은 질문 51번 → 바깥 서버 호출 0번 (나눠 쓰기)", calls.length === 0);
[st, h, b] = await go("/kis-check"); ok("kis-check: 값 없이 칸 이름만", !b.includes('"last":') && b.includes("fields"));
ok("kis-check: 키 안 보임", !b.includes("KISAPPKEY") && !b.includes("KISSECRET"));
[st, h, b] = await go("/health"); ok("health: 키 정보 안 보임", !b.includes("keys"));
const all = calls.map(c => c.url).filter(u => u.includes("koreainvestment"));
ok("한국투자증권엔 토큰·시세 주소만 감", all.every(u => /oauth2\/tokenP|\/quotations\//.test(u)));
// 주문 차단 함수 직접 확인
const src = (await import("fs")).readFileSync(new URL("../src/index.js", import.meta.url), "utf8");
const m = src.match(/const KIS_READ_ONLY[\s\S]*?\n}\n/)[0];
const kisAllowed = new Function(m.replace("const KIS_READ_ONLY", "var KIS_READ_ONLY") + "; return kisAllowed;")();
ok("주문 요청 차단 (국내 주식 주문)", !kisAllowed("/uapi/domestic-stock/v1/trading/order-cash", "TTTC0802U"));
ok("잔고 요청 차단", !kisAllowed("/uapi/domestic-stock/v1/trading/inquire-balance", "TTTC8434R"));
ok("해외 주문 차단", !kisAllowed("/uapi/overseas-stock/v1/trading/order", "TTTT1002U"));
ok("시세 tr_id를 주문 주소에 붙여도 차단", !kisAllowed("/uapi/domestic-stock/v1/trading/order-cash", "FHKST01010100"));
ok("정상 시세 요청은 허용", kisAllowed("/uapi/overseas-price/v1/quotations/price", "HHDFS00000300"));

// 긴급 정지 스위치
const envLock = { ...env, MAINTENANCE: "1" };
const goL = async (path) => { const r = await w.fetch(new Request("https://x.dev" + path), envLock, {waitUntil(){}}); return [r.status, await r.text()]; };
let [ls, lb] = await goL("/quote?s=NVDA"); ok("긴급 정지: 시세 멈춤 (503)", ls === 503);
[ls, lb] = await goL("/health"); ok("긴급 정지: 상태 확인은 됨", ls === 200 && lb.includes("lockdown"));

if (bad) { console.error(`보안 시험 ${bad}개 실패`); process.exit(1); }
console.log("보안 시험 모두 통과");
