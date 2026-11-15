"""앱에 넣는 ETF 목록 (한곳에서 관리). 종목코드·이름은 공공데이터(금융위원회 증권상품시세)에서 확인한 값이에요.
kind: index = 같은 지수를 따르는 미국 ETF(proxy) 가격으로 밤사이 변화를 계산 / pdf = 담긴 회사 비중 × 각 회사 가격으로 계산"""
GROUPS = {
    "sp":        {"name": "S&P500", "kind": "index", "proxy": "SPY"},
    "ndx":       {"name": "나스닥100", "kind": "index", "proxy": "QQQ"},
    "sox":       {"name": "필라델피아 반도체 지수", "kind": "index", "proxy": "SOXQ"},
    "semi":      {"name": "미국 반도체 (MVIS 25)", "kind": "index", "proxy": "SMH"},
    "div":       {"name": "미국배당다우존스", "kind": "index", "proxy": "SCHD"},
    "tech":      {"name": "미국 테크 TOP10 (Indxx)", "kind": "pdf", "proxy": ""},
    "bigtech":   {"name": "미국 빅테크 TOP7 Plus", "kind": "pdf", "proxy": ""},
    "space":     {"name": "미국 우주항공 TOP10", "kind": "pdf", "proxy": ""},
    "spacetech": {"name": "미국 우주테크 (Akros)", "kind": "pdf", "proxy": ""},
}
ETFS = [
    ("381180", "TIGER 미국필라델피아반도체나스닥", "sox"),
    ("390390", "KODEX 미국반도체", "semi"),
    ("360750", "TIGER 미국S&P500", "sp"), ("379800", "KODEX 미국S&P500", "sp"), ("360200", "ACE 미국S&P500", "sp"),
    ("379780", "RISE 미국S&P500", "sp"), ("0026S0", "1Q 미국S&P500", "sp"), ("433330", "SOL 미국S&P500", "sp"),
    ("133690", "TIGER 미국나스닥100", "ndx"), ("379810", "KODEX 미국나스닥100", "ndx"), ("367380", "ACE 미국나스닥100", "ndx"),
    ("368590", "RISE 미국나스닥100", "ndx"), ("0069M0", "1Q 미국나스닥100", "ndx"),
    ("458730", "TIGER 미국배당다우존스", "div"), ("446720", "SOL 미국배당다우존스", "div"), ("402970", "ACE 미국배당다우존스", "div"),
    ("381170", "TIGER 미국테크TOP10 INDXX", "tech"), ("465580", "ACE 미국빅테크TOP7 Plus", "bigtech"),
    ("0181L0", "SOL 미국우주항공TOP10", "space"), ("0183J0", "TIGER 미국우주테크", "spacetech"),
]


def isin(code):
    s = "KR7" + code + "00"
    digits = "".join(str(int(c, 36)) for c in s)
    tot = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch) * (2 if i % 2 == 0 else 1)
        tot += d // 10 + d % 10
    return s + str((10 - tot % 10) % 10)
