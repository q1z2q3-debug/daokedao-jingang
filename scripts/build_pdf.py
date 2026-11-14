# -*- coding: utf-8 -*-
"""把《润泽说 道可道之金刚经·通释》md 编成 A5 成书 PDF。

用法：python3 scripts/build_pdf.py
产物：book/润泽说 道可道之金刚经.pdf
依赖：weasyprint（纯 python，无需 LaTeX）
"""
import html as H
import pathlib
import re
import sys

try:
    from weasyprint import HTML
except ModuleNotFoundError:
    HTML = None

ROOT = pathlib.Path(__file__).resolve().parent.parent
MD = ROOT / "book" / "润泽说-道可道之金刚经·通释.md"
OUT = ROOT / "book" / "润泽说 道可道之金刚经.pdf"

sys.path.insert(0, str(ROOT / "scripts"))
from build_site import split_book, cn2int, md2html, FEN, ZONES, TITLE, VER  # noqa: E402

CSS = """
@page {
  size: A5;
  margin: 20mm 17mm 18mm;
  @bottom-center { content: counter(page); font-family: "Noto Serif CJK SC", serif; font-size: 8pt; color: #6B6152; }
  @top-center { content: "润泽说 道可道之金刚经"; font-family: "Noto Serif CJK SC", serif; font-size: 7.6pt; color: #A79C8B; letter-spacing: .1em; }
}
@page :first { @top-center { content: "" } @bottom-center { content: "" } }
@page cover { margin: 0; @top-center { content: "" } @bottom-center { content: "" } }

html, body { margin: 0; }
body { font-family: "Noto Serif CJK SC", serif; font-size: 9.6pt; line-height: 1.85; color: #25211D; }

/* 封面 */
.cover { page: cover; height: 210mm; padding: 26mm 20mm; box-sizing: border-box;
         border: 1px solid #DCD3C4; background: #FCFAF6; }
.cover .inner { border: 1px solid #EBE4D8; height: 100%; padding: 16mm 10mm; box-sizing: border-box; text-align: center; }
.cover .series { font-size: 8.4pt; letter-spacing: .34em; color: #7C6D5C; }
.cover h1 { font-size: 34pt; letter-spacing: .16em; margin: 34mm 0 4mm; font-weight: 700; line-height: 1.1; }
.cover .sub { font-size: 10pt; letter-spacing: .1em; color: #7C6D5C; }
.cover .rule { width: 14mm; height: .6mm; background: #944433; margin: 8mm auto 7mm; }
.cover .verse { font-size: 8.6pt; color: #6B6152; line-height: 2.1; letter-spacing: .05em; }
.cover .meta { margin-top: 30mm; font-size: 8.4pt; color: #7C6D5C; letter-spacing: .1em; }

/* 目录 */
.toc { page-break-before: always; column-count: 2; column-gap: 9mm; }
.toc h2 { font-size: 13pt; letter-spacing: .2em; color: #944433; text-align: center; margin: 2mm 0 6mm; font-weight: 600; }
.toc .zone { font-size: 8pt; color: #7C6D5C; letter-spacing: .14em; margin: 4mm 0 1mm; break-after: avoid; }
.toc a { display: block; text-decoration: none; color: #25211D; font-size: 8.8pt; margin: 1mm 0;
        border-bottom: 1px dotted #E1D9CB; }
.toc a::after { content: target-counter(attr(href), page); float: right; color: #7C6D5C; }

/* 正文 */
h1.part { page-break-before: always; font-size: 15pt; letter-spacing: .08em; margin: 0 0 2mm; color: #944433; font-weight: 600; }
h1.part .pn { display: block; font-size: 8pt; letter-spacing: .2em; color: #A79C8B; margin-bottom: 1mm; }
h2 { font-size: 11.2pt; margin: 6mm 0 2mm; padding-top: 3mm; border-top: .3pt solid #DCD3C4; color: #25211D; font-weight: 600; letter-spacing: .04em; }
h3 { font-size: 10pt; margin: 4mm 0 1.5mm; color: #944433; font-weight: 600; }
p { margin: 0 0 1.4mm; text-align: justify; text-indent: 2em; }
p.noind { text-indent: 0; }
blockquote { margin: 3mm 0; padding: 1mm 0 1mm 4mm; border-left: .7mm solid #944433; color: #3B352F; }
blockquote p { text-indent: 0; }
ul { margin: 1mm 0 2mm 6mm; padding: 0; }
li { font-size: 9.4pt; }
table { width: 100%; border-collapse: collapse; font-size: 8.2pt; margin: 2mm 0 3mm; page-break-inside: avoid; }
th, td { border: .3pt solid #DCD3C4; padding: 1.2mm 1.6mm; text-align: left; vertical-align: top; line-height: 1.6; }
th { background: #F1EAE0; font-weight: 600; }
hr { display: none; }
"""


def build():
    pre, blocks = split_book()
    fen, rest = {}, []
    for name, body in blocks:
        m = re.match(r"第([一二三四五六七八九十]+)分", name)
        if m:
            fen[cn2int(m.group(1))] = (name, body)
        else:
            rest.append((name, body))

    pre_clean = re.sub(r"## 目录\n.*?(?=\n## |\Z)", "", pre, count=1, flags=re.S)

    parts = []
    for i, name, slug in FEN:
        nm, body = fen.get(i, (name, ""))
        body = re.sub(r"^### ", "## ", body, flags=re.M)
        parts.append(f'<h1 class="part" id="fen{i}"><span class="pn">第 {i} 分</span>{H.escape(nm[3:] if nm.startswith("第") else nm)}</h1>'
                     f"{md2html(body)}")
    body_html = "\n".join(parts)

    after = next((b for n, b in rest if n.startswith("后记")), "")
    apps = [(n, b) for n, b in rest if n.startswith("附录")]
    after_html = f'<h1 class="part" id="after"><span class="pn">后记</span>一部可以日日使用的经</h1>' + md2html(after)
    apps_html = '<h1 class="part" id="app"><span class="pn">附录</span>附录五篇</h1>' + \
                "".join(f"<h2>{H.escape(n)}</h2>{md2html(b)}" for n, b in apps)
    pre_html = f'<h1 class="part" id="pre"><span class="pn">卷首</span>体例与总纲</h1>' + md2html(re.sub(r"^## ", "## ", pre_clean, flags=re.M))

    toc = ['<div class="toc"><h2>目 录</h2>',
           '<p class="noind" style="font-size:8.4pt;color:#7C6D5C;text-indent:0">卷首 · 体例与总纲</p>',
           '<a href="#pre">体例与总纲</a>']
    for zname, a, b, _ in ZONES:
        toc.append(f'<div class="zone">{zname}</div>')
        for i, name, slug in FEN:
            if a <= i <= b:
                toc.append(f'<a href="#fen{i}">第{i}分　{name[:-1]}</a>')
    toc += ['<div class="zone">附</div><a href="#after">后记：一部可以日日使用的经</a>',
            '<a href="#app">附录五篇</a>', "</div>"]
    toc = "\n".join(toc)

    html = f"""<!DOCTYPE html><html lang="zh-Hans"><head><meta charset="utf-8">
<title>{TITLE}</title><style>{CSS}</style></head><body>
<div class="cover"><div class="inner">
<div class="series">润泽说　道可道</div>
<h1>金刚经</h1>
<div class="sub">《金刚般若波罗蜜经》三十二分通释</div>
<div class="rule"></div>
<div class="verse">凡所有相，皆是虚妄。<br>若见诸相非相，即见如来。</div>
<div class="meta">润泽　著　·　v{VER}　·　CC BY-NC-SA 4.0</div>
</div></div>
{toc}
{pre_html}
{body_html}
{after_html}
{apps_html}
</body></html>"""

    tmp = ROOT / "book" / "_print.html"
    tmp.write_text(html, encoding="utf-8")
    if HTML is not None:
        HTML(string=html, base_url=str(ROOT)).write_pdf(str(OUT))
    else:
        import subprocess
        subprocess.run(["weasyprint", "--base-url", str(ROOT), str(tmp), str(OUT)], check=True)
    tmp.unlink(missing_ok=True)
    import fitz
    doc = fitz.open(str(OUT))
    print(f"built {OUT.name} {OUT.stat().st_size/1e6:.1f} MB, {doc.page_count} pages")


if __name__ == "__main__":
    build()
