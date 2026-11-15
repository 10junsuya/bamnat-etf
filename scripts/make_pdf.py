"""마크다운 → 노몬 스타일 PDF (Conrad의 브리핑·회의록용).

python3 scripts/make_pdf.py 입력.md 출력.pdf ["제목"]
크롬(google-chrome 또는 chromium)으로 인쇄해요. 한글 글꼴(Noto Sans CJK)이 필요해요.
"""
import html
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CSS = """@page{size:A4;margin:18mm 16mm}
body{font-family:'Noto Sans CJK KR','Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif;font-size:10.5pt;line-height:1.6;color:#1D1D1F;word-break:keep-all}
h1{font-size:18pt;margin:0 0 4pt;padding-bottom:8pt;border-bottom:2px solid #9A7B3C}
h2{font-size:13pt;margin:18pt 0 6pt}
h2::before{content:'';display:inline-block;width:4px;height:12pt;background:#9A7B3C;margin-right:7px;vertical-align:-2px}
h3{font-size:11pt;margin:12pt 0 4pt}
table{border-collapse:collapse;width:100%;margin:6pt 0;font-size:9.5pt} th{background:#F5F5F7;text-align:left}
th,td{border:1px solid #E5E5EA;padding:5pt 6pt;vertical-align:top}
code{background:#F5F5F7;padding:0 3px;border-radius:3px;font-size:9pt}
ul,ol{padding-left:16pt} li{margin:2pt 0} a{color:#1D1D1F}
.ft{margin-top:24pt;font-size:8.5pt;color:#8E8E93;border-top:1px solid #E5E5EA;padding-top:6pt}"""


def to_html(md_text):
    try:
        import markdown  # type: ignore
        return markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"])
    except ImportError:
        pandoc = shutil.which("pandoc")
        if pandoc:
            return subprocess.run([pandoc, "-f", "gfm", "-t", "html"], input=md_text, capture_output=True, text=True, check=True).stdout
        return "<pre>" + html.escape(md_text) + "</pre>"


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    title = sys.argv[3] if len(sys.argv) > 3 else src.stem
    body = to_html(src.read_text(encoding="utf-8"))
    doc = f"<!doctype html><html lang=ko><meta charset=utf-8><title>{html.escape(title)}</title><style>{CSS}</style><body>{body}<div class=ft>노몬 · GNOMON</div></body></html>"
    chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not chrome:
        print("크롬을 찾지 못했어요. PDF 대신 마크다운으로 보고해 주세요.")
        return 1
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(doc)
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={out.resolve()}", f"file://{f.name}"], capture_output=True, timeout=120)
    if not out.exists():
        print("PDF를 만들지 못했어요:", r.stderr.decode(errors="ignore")[:300])
        return 1
    print(f"PDF 만들었어요: {out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
