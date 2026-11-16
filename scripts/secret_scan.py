"""저장소 보안 검사: 키·토큰·비밀번호·개인정보가 공개 저장소에 올라가지 않았는지 찾아요.

python3 scripts/secret_scan.py   → 문제가 있으면 무엇이 어디 있는지 출력하고 실패(1)로 끝나요.
GitHub에서 올릴 때마다 자동으로 돌아요(.github/workflows/security.yml). 찾은 값 자체는 출력하지 않아요.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RULES = [
    ("GitHub 토큰", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}")),
    ("Anthropic 키", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}")),
    ("OpenAI 계열 키", re.compile(r"\bsk-(proj-)?[A-Za-z0-9]{32,}")),
    ("AWS 키", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Slack 토큰", re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}")),
    ("Google API 키", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("개인 키 파일", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY")),
    ("주소에 들어간 키", re.compile(r"[?&](token|apikey|api_key|appkey|appsecret|serviceKey|crtfc_key|auth)=[A-Za-z0-9%/+_\-]{12,}", re.I)),
    ("코드에 적힌 키·비밀번호", re.compile(
        r"""(api[_-]?key|app[_-]?key|app[_-]?secret|secret[_-]?key|access[_-]?token|client[_-]?secret|password|passwd)\s*[:=]\s*["'][A-Za-z0-9/+_\-]{16,}["']""", re.I)),
    ("한국 주민등록번호 모양", re.compile(r"\b\d{6}-[1-4]\d{6}\b")),
    ("휴대폰 번호", re.compile(r"\b01[016789]-?\d{3,4}-?\d{4}\b")),
    ("개인 메일 주소", re.compile(r"\b[A-Za-z0-9._%+\-]+@(gmail|naver|kakao|daum|hanmail|nate|outlook|hotmail|icloud|yahoo)\.(com|net|co\.kr)\b", re.I)),
]
# 괜찮은 것(예시·자동 계정)
ALLOW = re.compile(r"noreply|no-reply|example\.(com|org)|users\.noreply\.github\.com|\$\{\{|secrets\.|process\.env|env\.[A-Z_]+|os\.environ", re.I)
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico", ".woff", ".woff2", ".zip"}


def files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
    return [ROOT / f for f in out if f and Path(f).suffix.lower() not in SKIP_EXT]


def main():
    found = []
    for p in files():
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.split("\n"), 1):
            if len(line) > 5000:  # 데이터 한 줄이 아주 긴 파일은 잘라서 봐요
                chunks = [line[i:i + 5000] for i in range(0, len(line), 4800)]
            else:
                chunks = [line]
            for ch in chunks:
                for name, rx in RULES:
                    for m in rx.finditer(ch):
                        ctx = ch[max(0, m.start() - 40):m.end() + 40]
                        if ALLOW.search(ctx):
                            continue
                        # 숫자 데이터(가격·날짜 등)를 전화번호로 잘못 보는 것 방지: 하이픈 없는 11자리는 앞뒤가 숫자·소수점이면 넘어가요
                        if name == "휴대폰 번호" and "-" not in m.group(0):
                            continue
                        found.append(f"{p.relative_to(ROOT)}:{n} → {name}")
    if found:
        print("보안 검사 실패: 공개 저장소에 올라가면 안 되는 값이 있어요 (값 자체는 출력하지 않아요)")
        for f in sorted(set(found)):
            print(" - " + f)
        print("→ 키는 GitHub Secrets / Cloudflare 비밀값으로만, 개인정보는 저장소에 적지 마세요.")
        return 1
    print("보안 검사 통과: 키·토큰·개인정보가 보이지 않아요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
