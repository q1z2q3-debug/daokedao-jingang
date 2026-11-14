# -*- coding: utf-8 -*-
"""把《金刚经》md 母本编译成单文件 HTML 阅读版（无外链、无脚本）。
用法：python3 scripts/build_html.py
输入：book/润泽说-道可道之金刚经·通释.md
输出：book/金刚经·阅读版.html
"""
import pathlib, re, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import daokedao_book as kit

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"
MD = BOOK / "润泽说-道可道之金刚经·通释.md"
OUT = BOOK / "金刚经·阅读版.html"
TMP = pathlib.Path("/tmp/jingang_src.md")
BODY_TMP = pathlib.Path("/tmp/jingang_body.html")

src = MD.read_text(encoding="utf-8")

# ---------- 1) 预处理 ----------
src = re.sub(r"^---\n.*?\n---\n", "", src, count=1, flags=re.S)
src = src.replace("# 润泽说 道可道之金刚经\n## 《金刚般若波罗蜜经》通释\n", "")
src = re.sub(r"## 目录\n.*?\n---\n", "", src, count=1, flags=re.S)
src = src.replace("\n---\n# ", "\n\nSPLIT\n\n# ")
# 附录 / 后记 内的二级小标题降为三级
src = re.sub(r"^## ((?:弁言|[一二三四五六七八九十]+、)[^\n]*|这一部书的用法|关于[^\n]*|一页纸[^\n]*)",
             r"### \1", src, flags=re.M)
src = re.sub(r"^# (第[一二三四五六七八九十]+分|后记|附录)", r"## \1", src, flags=re.M)
src = src.replace("\nSPLIT\n", "\n\n---\n")
TMP.write_text(src, encoding="utf-8")

# ---------- 2) pandoc ----------
subprocess.run(["pandoc", str(TMP), "-f", "markdown+hard_line_breaks",
                "-t", "html5", "--no-highlight", "-o", str(BODY_TMP)], check=True)
body = BODY_TMP.read_text(encoding="utf-8")

# ---------- 3) 后处理 ----------
body = re.sub(r"<h([23])\s*\n\s*", r"<h\1 ", body)

heads = re.findall(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', body, flags=re.S)
nav_items = []
for hid, raw in heads:
    txt = re.sub(r"<[^>]+>", "", raw).strip()
    txt = re.sub(r"\s+", " ", txt)
    m = re.match(r"^(第[一二三四五六七八九十]+分)\s+(.+)$", txt)
    if m:
        idx = m.group(1).replace("第", "").replace("分", "")
        nav_items.append('<li><a href="#%s"><i>%s</i><span>%s</span></a></li>'
                         % (hid, idx, m.group(2)))
    elif txt.startswith(("序", "后记", "附录")):
        nav_items.append('<li class="wide"><a href="#%s"><i>·</i><span>%s</span></a></li>'
                         % (hid, txt))
nav = "\n".join(nav_items)

def part(m):
    hid, txt = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
    m2 = re.match(r"^(第[一二三四五六七八九十]+分)\s+(.+)$", txt)
    if not m2:
        return m.group(0)
    return ('<h2 class="part" id="%s"><span class="pn">%s</span>'
            '<span class="pt">%s</span></h2>') % (hid, m2.group(1), m2.group(2))

body = re.sub(r'<h2 id="([^"]+)">(.*?)</h2>', part, body, flags=re.S)
body = body.replace("<blockquote>", '<blockquote class="sutra">')
body = body.replace("<table>", '<table class="t">')

FAVICON = ("<link rel=\"icon\" type=\"image/svg+xml\" href=\"data:image/svg+xml,"
           "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
           "%3Crect width='64' height='64' fill='%23994433'/%3E"
           "%3Ctext x='32' y='46' font-size='32' text-anchor='middle' "
           "fill='%23F7F4EE' font-family='serif'%3E%E9%87%91%3C/text%3E%3C/svg%3E\">")

CSS = """
:root{--paper:#F7F4EE;--paper2:#FCFAF6;--ink:#25211D;--ink2:#3B352F;--ochre:#994433;--brown:#7C6D5C;--line:#DCD5C8;}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:"Noto Serif SC","Songti SC","Source Han Serif SC",serif;
  -webkit-font-smoothing:antialiased;line-height:1.95;}
.page{max-width:780px;margin:0 auto;padding:56px 28px 80px;}

.toc{background:var(--paper2);border:1px solid var(--line);padding:22px 24px;margin-bottom:52px;}
.toc h4{margin:0 0 14px;font-size:13px;letter-spacing:.22em;color:var(--brown);font-weight:400;}
.toc ol{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:2px 20px;}
.toc li a{display:flex;gap:9px;align-items:baseline;text-decoration:none;color:var(--ink);
  font-size:14px;padding:5px 0;border-bottom:1px dotted #E4DDD0;}
.toc li a:hover{color:var(--ochre);}
.toc li.wide{grid-column:1/-1;}
.toc li.wide a{border-bottom:1px solid #E4DDD0;margin-top:6px;color:var(--brown);letter-spacing:.06em;}
.toc i{font-style:normal;font-size:11.5px;color:var(--ochre);min-width:20px;text-align:right;}

h2{font-size:24px;font-weight:700;letter-spacing:.06em;margin:56px 0 24px;
  padding-top:20px;border-top:1px solid var(--line);}
h2::before{content:"";display:block;width:30px;height:2px;background:var(--ochre);margin:0 0 16px;}
h2.part{display:flex;flex-direction:column;gap:6px;padding-top:26px;margin-top:72px;}
h2.part::before{margin-bottom:14px;}
h2.part .pn{font-size:13px;font-weight:400;letter-spacing:.3em;color:var(--brown);}
h2.part .pt{font-size:27px;letter-spacing:.1em;}
h3{font-size:15px;font-weight:600;letter-spacing:.14em;color:var(--ochre);
  margin:30px 0 10px;display:flex;align-items:center;gap:10px;}
h3::after{content:"";flex:1;height:1px;background:#EAE3D6;}

p{margin:0 0 1.02em;font-size:17px;color:var(--ink2);text-align:justify;}
ul{margin:0 0 16px;padding-left:0;list-style:none;}
li{font-size:16.5px;color:var(--ink2);margin-bottom:8px;padding-left:16px;position:relative;text-align:justify;}
li::before{content:"";position:absolute;left:0;top:.85em;width:5px;height:5px;background:#C9B7A4;border-radius:50%;}
ol{margin:0 0 16px;padding-left:1.8em;}
ol li{padding-left:0;}
ol li::before{content:none;}

blockquote.sutra{margin:24px 0 28px;padding:18px 22px;background:#FBF3EE;
  border-left:3px solid var(--ochre);}
blockquote.sutra p{margin:0 0 .62em;font-size:16px;line-height:2.05;color:#4A4139;letter-spacing:.03em;}
blockquote.sutra p:last-child{margin-bottom:0;}
blockquote.sutra p strong{color:var(--ochre);font-weight:600;}

table.t{width:100%;border-collapse:collapse;margin:14px 0 26px;font-size:14px;}
table.t th,table.t td{border:1px solid var(--line);padding:9px 11px;text-align:left;
  vertical-align:top;line-height:1.72;word-break:break-word;}
table.t th{background:#F1EAE0;font-weight:600;color:var(--ink);}
table.t td{color:var(--ink2);}

.foot{margin-top:68px;padding-top:24px;border-top:1px solid var(--line);text-align:center;
  font-size:13px;color:var(--brown);letter-spacing:.1em;line-height:2.1;}

@media (max-width:640px){
  .page{padding:30px 17px 54px;}
  .toc ol{grid-template-columns:1fr;}
  h2.part .pt{font-size:22px;}
  h2{font-size:21px;margin-top:42px;}
  p{font-size:16px;}
  li{font-size:15.3px;}
  table.t{font-size:12.5px;display:block;overflow-x:auto;white-space:nowrap;}
}

"""
CSS = CSS + kit.COVER_CSS + kit.FIG_CSS + """
"""

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
__FAVICON__
<title>润泽说 道可道之金刚经 · 阅读版</title>
<style>__CSS__</style>
</head>
<body>
<div class="page">
  <section class="cover">
    <div class="series">润 泽 说 · 道 可 道</div>
    <div class="stage">
      <div class="gatha l">如露亦如电<br>应作如是观</div>
      <div class="center">
        <h1>金刚般若</h1>
        <div class="sub">《金刚般若波罗蜜经》三十二分通释</div>
        <div class="tag">三 十 二 分</div>
        <div class="seal">金</div>
      </div>
      <div class="gatha r">一切有为法<br>如梦幻泡影</div>
    </div>
    <div class="meta"><span>姚秦鸠摩罗什译本</span><span>般若三段范式</span><span>三才五蕴太极空杯</span><span>二〇二六年十一月</span></div>
  </section>

  <div class="frontis">
    <div class="fseries">润 泽 说 · 道 可 道</div>
    <div class="ftitle">金刚般若</div>
    <div class="fsub">《金刚般若波罗蜜经》三十二分通释</div>
    <div class="frule"></div>
    <div class="fname">润　泽　著</div>
    <div class="fmeta">底本　姚秦三藏法师鸠摩罗什译本（通行本）<br>体例　三十二分 · 每分七段<br>范式　佛说A · 即非A · 是名A<br>版本　v1.1 · 二〇二六年十一月</div>
    <div class="fseal">金</div>
  </div>
  <nav class="toc"><h4>目　录</h4><ol>__NAV__</ol></nav>
  <main>__BODY__</main>
  <div class="foot">润泽说 道可道之金刚经 · 通释<br>不取于相，如如不动</div>
</div>
</body>
</html>"""

html_out = (HTML.replace("__CSS__", CSS).replace("__NAV__", nav)
            .replace("__BODY__", body).replace("__FAVICON__", FAVICON))
OUT.write_text(html_out, encoding="utf-8")
print("ok", len(html_out), "chars |", len(nav_items), "toc items |", OUT)
