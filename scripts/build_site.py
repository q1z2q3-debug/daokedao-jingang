# -*- coding: utf-8 -*-
"""从 book/润泽说-道可道之金刚经·通释.md 生成 docs/ 静态站
（首页、卷首、篇目、32 分逐页、后记、附录、下载页、sitemap、llms.txt）。

用法：python3 scripts/build_site.py
"""
import html as H
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"
MD = BOOK / "润泽说-道可道之金刚经·通释.md"
DOCS = ROOT / "docs"

SITE = "https://q1z2q3-debug.github.io/daokedao-jingang"
SERIES = "润泽说 道可道"
TITLE = "润泽说 道可道之金刚经"
VER = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DOI = "10.5281/zenodo.00000000"  # 存缴后回填；为占位时页脚不显示 DOI

# 三十二分：(序数, 分题, slug)
FEN = [
    (1, "法会因由分", "fahuyinyou"), (2, "善现启请分", "shanxianqiqing"),
    (3, "大乘正宗分", "dachengzhengzong"), (4, "妙行无住分", "miaoxingwuzhu"),
    (5, "如理实见分", "rulishijian"), (6, "正信希有分", "zhengxinxiyou"),
    (7, "无得无说分", "wudewushuo"), (8, "依法出生分", "yifachusheng"),
    (9, "一相无相分", "yixiangwuxiang"), (10, "庄严净土分", "zhuangyanjingtu"),
    (11, "无为福胜分", "wuweifusheng"), (12, "尊重正教分", "zunzhongzhengjiao"),
    (13, "如法受持分", "rufashouchi"), (14, "离相寂灭分", "lixiangjimie"),
    (15, "持经功德分", "chijinggongde"), (16, "能净业障分", "nengjingyezhang"),
    (17, "究竟无我分", "jiujingwuwo"), (18, "一体同观分", "yititongguan"),
    (19, "法界通化分", "fajietonghua"), (20, "离色离相分", "liselixiang"),
    (21, "非说所说分", "feishuosuoshuo"), (22, "无法可得分", "wufakede"),
    (23, "净心行善分", "jingxinxingshan"), (24, "福智无比分", "fuzhiwubi"),
    (25, "化无所化分", "huawusuohua"), (26, "法身非相分", "fashenfeixiang"),
    (27, "无断无灭分", "wuduanwumie"), (28, "不受不贪分", "bushoubutan"),
    (29, "威仪寂静分", "weiyijingjing"), (30, "一合理相分", "yihelixiang"),
    (31, "知见不生分", "zhijianbusheng"), (32, "应化非真分", "yinghuafeizhen"),
]
SLUG = {name: slug for _, name, slug in FEN}

# 三分判摄
ZONES = [("序分", 1, 2, "发起与启请：佛在舍卫城乞食、洗足、敷座，须菩提问「云何应住、云何降伏其心」。"),
         ("正宗分", 3, 31, "破四相、破法执、明无住、辨福德、显实相——二十九分只为拆开一个「住」字。"),
         ("流通分", 32, 32, "应化非真：一切有为法如梦幻泡影，经止于此。")]

CSS = """
:root{--paper:#F7F4EE;--paper2:#FCFAF6;--ink:#25211D;--ink2:#3B352F;--muted:#6B6152;--line:#DCD3C4;--accent:#944433}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:"Noto Serif SC","Songti SC",Georgia,serif;font-size:16px;line-height:1.9;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid rgba(148,68,51,.28)}
a:hover{border-bottom-color:var(--accent)}
.wrap{max-width:900px;margin:0 auto;padding:0 28px}
header.top{border-bottom:1px solid var(--line);position:sticky;top:0;z-index:9;background:rgba(247,244,238,.94)}
header.top .wrap{display:flex;align-items:baseline;justify-content:space-between;gap:14px;padding:14px 0;flex-wrap:wrap}
.brand{font-size:15px;letter-spacing:.12em;border:0;white-space:nowrap}
nav{display:flex;flex-wrap:wrap;column-gap:16px;row-gap:2px;justify-content:flex-end}
nav a{font-size:13px;color:var(--muted);border:0;white-space:nowrap;font-family:"Noto Sans SC",sans-serif;letter-spacing:.04em}
nav a.on,nav a:hover{color:var(--accent)}
main{padding:52px 0 40px}
.eyebrow{font-family:"Noto Sans SC",sans-serif;font-size:12px;letter-spacing:.22em;color:var(--muted)}
h1{font-size:38px;line-height:1.32;font-weight:600;margin:14px 0 8px}
h2{font-size:21px;font-weight:600;margin:48px 0 16px;padding-top:18px;border-top:1px solid var(--line)}
h3{font-size:17px;font-weight:600;margin:24px 0 8px}
p{margin:0 0 14px}
.lede{font-size:17.5px;color:#3A342C;max-width:730px}
.small{font-size:13.5px;color:var(--muted);font-family:"Noto Sans SC",sans-serif;line-height:1.8}
.list{border-top:1px solid var(--line)}
.row{display:grid;grid-template-columns:56px 1fr 150px;gap:18px;padding:18px 0;border-bottom:1px solid var(--line);align-items:start}
.row .no{font-family:"Noto Sans SC",sans-serif;font-size:12px;color:var(--muted);letter-spacing:.1em;padding-top:6px}
.row h3{margin:0 0 4px;font-size:18px}
.row .go{text-align:right;font-size:13px}
article{border-top:1px solid var(--line);padding-top:26px}
article h3{font-size:18px;letter-spacing:.04em;color:var(--accent)}
article h4{font-size:15.5px;margin:20px 0 6px}
article p{text-align:justify}
blockquote{margin:22px 0;padding:4px 0 4px 18px;border-left:2px solid var(--accent);color:#3A342C}
ul{margin:0 0 14px 18px;padding:0}
table{width:100%;border-collapse:collapse;font-size:14px;margin:14px 0}
th,td{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top;line-height:1.7}
th{background:#F1EAE0;font-weight:600}
.prevnext{display:flex;justify-content:space-between;gap:16px;margin:44px 0 0;padding-top:18px;border-top:1px solid var(--line);font-size:14px}
footer{border-top:1px solid var(--line);padding:30px 0 56px;margin-top:44px}
footer .wrap{display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap}
@media(max-width:720px){
 header.top .wrap{padding:12px 18px;gap:10px}.wrap{padding:0 18px}.brand{font-size:12.5px;letter-spacing:.04em}nav{column-gap:8px}nav a{font-size:11px;letter-spacing:0}
 h1{font-size:28px}main{padding-top:34px}.row{grid-template-columns:1fr;gap:4px}.row .no{display:none}.row .go{text-align:left}
 .prevnext{flex-direction:column;gap:6px}
}
"""

NAV = [("/", "首页", "home"), ("/book.html", "全书", "book"), ("/chapters/", "三十二分", "chapters"),
       ("/afterword.html", "后记", "afterword"), ("/downloads/", "下载", "downloads")]


def head(title, desc, path, jsonld=None, act="home"):
    ld = ""
    if jsonld:
        ld = '<script type="application/ld+json">%s</script>' % json.dumps(jsonld, ensure_ascii=False, separators=(",", ":"))
    nav = "".join(f'<a href="{SITE}{p}" class="{"on" if a == act else ""}">{n}</a>' for p, n, a in NAV)
    return f"""<!DOCTYPE html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H.escape(title)}</title>
<meta name="description" content="{H.escape(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SERIES}">
<meta property="og:title" content="{H.escape(title)}">
<meta property="og:description" content="{H.escape(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/favicon.svg">
<meta name="author" content="润泽">
<link rel="icon" type="image/svg+xml" href="{SITE}/favicon.svg">
<link rel="stylesheet" href="https://miaoda.feishu.cn/fonts/css2?family=Noto+Serif+SC:wght@400;500;600;700&family=Noto+Sans+SC:wght@300;400;500&display=swap">
<style>{CSS}</style>
{ld}
</head>
<body>
<header class="top"><div class="wrap">
<a class="brand" href="{SITE}/"><b>润泽说</b> · 道可道</a>
<nav>{nav}</nav>
</div></header>
"""


def foot():
    doi = f'　·　<a href="https://doi.org/{DOI}">DOI</a>' if not DOI.endswith("00000000") else ""
    return f"""<footer><div class="wrap">
<div class="small">{SERIES}之金刚经　·　v{VER}　·　CC BY-NC-SA 4.0<br><a href="{SITE}/llms.txt">llms.txt</a>　·　<a href="{SITE}/sitemap.xml">sitemap</a></div>
<div class="small"><a href="https://github.com/q1z2q3-debug/daokedao-jingang">GitHub</a>{doi}　·　<a href="https://q1z2q3-debug.github.io/runze-daokedao/">系列总站</a></div>
</div></footer>
</body></html>
"""


def inline(t):
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t


def md2html(src):
    """轻量 md → html：段落、li、blockquote、表格、h3/h4。"""
    out, bufq, bufl, buft = [], [], [], []

    def flush():
        nonlocal bufq, bufl, buft
        if bufq:
            out.append("<blockquote>" + "".join(f"<p>{x}</p>" for x in bufq) + "</blockquote>")
            bufq = []
        if bufl:
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in bufl) + "</ul>")
            bufl = []
        if buft:
            raw = [r for r in buft if not re.match(r"^\|?[\s:|-]+\|$", r)]
            rows = [[inline(H.escape(c.strip())) for c in r.strip().strip("|").split("|")] for r in raw]
            th = "".join(f"<th>{c}</th>" for c in rows[0])
            tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>")
            buft = []

    for raw in src.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            flush(); continue
        if line.strip().startswith("|"):
            if bufq or bufl: flush()
            buft.append(line.strip())
            continue
        else:
            flush()
        if line.startswith("#### "):
            out.append(f"<h4>{inline(H.escape(line[5:]))}</h4>"); continue
        if line.startswith("### "):
            out.append(f"<h4>{inline(H.escape(line[4:]))}</h4>"); continue
        if line == "---" or line == ">":
            continue
        if line.startswith(">"):
            if bufl: flush()
            t = line[1:].lstrip()
            if t: bufq.append(inline(H.escape(t)))
            continue
        if line.startswith("- "):
            if bufq: flush()
            bufl.append(inline(H.escape(line[2:])))
            continue
        out.append(f"<p>{inline(H.escape(line))}</p>")
    flush()
    return "".join(out)


CN = "一二三四五六七八九十"


def parse():
    """切出卷首、32 分、后记、附录。"""
    src = MD.read_text(encoding="utf-8")
    src = re.sub(r"^# 润泽说 道可道之金刚经\n## 《金刚般若波罗蜜经》通释\n", "", src, count=1)
    lines = src.split("\n")
    blocks, cur, title = [], [], None
    for ln in lines:
        m = re.match(r"^# (第[一二三四五六七八九十]+分|后记|附录[一二三四五六])[： ]*(.*)$", ln)
        if m:
            if title is not None:
                blocks.append((title, "\n".join(cur)))
            title, cur = (m.group(1) + (" " + m.group(2) if m.group(2) else "")), []
            continue
        if title is None:
            cur.append(ln)          # 卷首
        else:
            cur.append(ln)
    if title is not None:
        blocks.append((title, "\n".join(cur)))
    front = "\n".join(cur) if title is None else blocks[0][1] if blocks and blocks[0][0] is None else ""
    return src, blocks


def split_book():
    src = MD.read_text(encoding="utf-8")
    src = re.sub(r"^# 润泽说 道可道之金刚经\n## 《金刚般若波罗蜜经》通释\n", "", src, count=1)
    pre, blocks, cur, title = [], [], [], None

    def push():
        if title is not None:
            blocks.append((title, "\n".join(cur)))

    for ln in src.split("\n"):
        m = re.match(r"^# (第[一二三四五六七八九十]+分|后记|附录[一二三四五六七八九十]+)[： ]*(.*)$", ln)
        if m:
            push_cur = None
            if title is not None:
                blocks.append((title, "\n".join(cur)))
            title = (m.group(1) + (" · " + m.group(2) if m.group(2) else ""))
            cur = []
        else:
            if title is None:
                pre.append(ln)
            else:
                cur.append(ln)
    if title is not None:
        blocks.append((title, "\n".join(cur)))
    return "\n".join(pre), blocks


def cn2int(s):
    if s == "十": return 10
    if "十" in s:
        a, _, b = s.partition("十")
        return (CN.index(a) + 1 if a else 1) * 10 + (CN.index(b) + 1 if b else 0)
    return CN.index(s) + 1


def build():
    pre, blocks = split_book()
    DOCS.mkdir(exist_ok=True)
    (DOCS / "chapters").mkdir(exist_ok=True)
    (DOCS / "downloads").mkdir(exist_ok=True)

    fen, rest = {}, []
    for name, body in blocks:
        m = re.match(r"第([一二三四五六七八九十]+)分", name)
        if m:
            n = cn2int(m.group(1))
            fen[n] = (name, body)
        else:
            rest.append((name, body))

    # 卷首：去掉「目录」一节（篇目页承担）
    pre_clean = re.sub(r"## 目录\n.*?(?=\n## |\Z)", "", pre, count=1, flags=re.S)
    pre_clean = pre_clean.replace("## 体例与总纲", "### 体例与总纲")

    recs = []
    for i, t, slug in FEN:
        body = fen.get(i, ("", ""))[1]
        wc = len(re.sub(r"\s", "", body))
        recs.append(dict(i=i, name=t, slug=slug, body=body, wc=wc))

    # ---- 32 分逐页 ----
    for k, r in enumerate(recs):
        fn = f"{r['i']:02d}-{r['slug']}.html"
        prev = nxt = ""
        if k > 0:
            p = recs[k - 1]
            prev = f'<a href="{SITE}/chapters/{p["i"]:02d}-{p["slug"]}.html">← 第{p["i"]}分 {p["name"][:-1]}</a>'
        if k < len(recs) - 1:
            nx = recs[k + 1]
            nxt = f'<a href="{SITE}/chapters/{nx["i"]:02d}-{nx["slug"]}.html">第{nx["i"]}分 {nx["name"][:-1]} →</a>'
        zone = next(z[0] for z in ZONES if z[1] <= r["i"] <= z[2])
        desc = f"《金刚经》第{r['i']}分 {r['name'][:-1]}：原文底本、分题释义、字源与名相、逐段深解、俗见勘破、般若范式。{r['wc']} 字。"
        ld = {"@context": "https://schema.org", "@type": "Article",
              "headline": f"第{r['i']}分 {r['name'][:-1]}｜{TITLE}",
              "url": f"{SITE}/chapters/{fn}", "inLanguage": "zh-Hans", "wordCount": r["wc"],
              "author": {"@type": "Person", "name": "润泽"},
              "isPartOf": {"@type": "Book", "@id": f"{SITE}/book.html#book"}}
        (DOCS / "chapters" / fn).write_text(
            head(f"第{r['i']}分 {r['name'][:-1]}｜{TITLE}", desc, f"/chapters/{fn}", ld, act="chapters") +
            f"""<main><div class="wrap">
<p class="eyebrow">{zone}　·　第 {r['i']} 分　·　{r['wc']} 字</p>
<h1>{H.escape(r['name'][:-1])}</h1>
<p class="small">底本：姚秦鸠摩罗什译《金刚般若波罗蜜经》，通行字句，异读另注　·　<a href="{SITE}/book.html">全书阅读版</a>　·　<a href="{SITE}/chapters/">三十二分</a></p>
<article>{md2html(r['body'])}</article>
<div class="prevnext">{prev}<a href="{SITE}/chapters/">三十二分</a>{nxt}</div>
</div></main>""" + foot(), encoding="utf-8")

    # ---- 卷首 ----
    (DOCS / "preface.html").write_text(
        head(f"卷首 · 体例与总纲｜{TITLE}",
             "《金刚经》通释的体例、三分判摄与底本说明：一分七段，另加「即非」三层拆解。",
             "/preface.html", None, act="home") +
        f"""<main><div class="wrap">
<p class="eyebrow">卷首</p>
<h1>体例与总纲</h1>
<p class="lede">全书只做一件事：把「佛说 A — 即非 A — 是名 A」这把尺子逐分拆开，让经文自己把般若讲出来。</p>
<article>{md2html(pre_clean)}</article>
<div class="prevnext"><a href="{SITE}/chapters/">三十二分</a><a href="{SITE}/book.html">全书 →</a></div>
</div></main>""" + foot(), encoding="utf-8")

    # ---- 三十二分篇目 ----
    secs = []
    for zname, a, b, zdesc in ZONES:
        grp = [r for r in recs if a <= r["i"] <= b]
        secs.append(f"<h2>{zname}　<span class='small'>{len(grp)} 分</span></h2><p class='small'>{zdesc}</p><div class='list'>")
        for r in grp:
            secs.append(f"""<div class="row"><div class="no">{r['i']:02d}</div>
<div><h3><a href="{SITE}/chapters/{r['i']:02d}-{r['slug']}.html">{r['name'][:-1]}</a></h3>
<p class="small" style="margin:0;">{r['wc']} 字　·　<span>{r['name']}</span></p></div>
<div class="go"><a href="{SITE}/chapters/{r['i']:02d}-{r['slug']}.html">读这一分</a></div></div>""")
        secs.append("</div>")
    idx_ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"{TITLE} · 三十二分",
              "url": f"{SITE}/chapters/", "inLanguage": "zh-Hans",
              "isPartOf": {"@type": "Book", "@id": f"{SITE}/book.html#book"},
              "hasPart": [{"@type": "Article", "name": r["name"], "url": f"{SITE}/chapters/{r['i']:02d}-{r['slug']}.html"}
                          for r in recs]}
    (DOCS / "chapters" / "index.html").write_text(
        head(f"三十二分｜{TITLE}",
             "《金刚经》三十二分全目：序分二分、正宗分二十九分、流通分一分。一分一页，可单独引用。",
             "/chapters/", idx_ld, act="chapters") +
        f"""<main><div class="wrap">
<p class="eyebrow">金刚经 · 三十二分</p>
<h1>一分一页，三十二分</h1>
<p class="lede">昭明太子分经为三十二，本书逐分独立成页。每分七段同构：原文底本、分题释义、字源与名相、逐段深解、俗见勘破、般若范式与跨典互参、小结。凡「如来说〇〇，即非〇〇，是名〇〇」句式，另拆随俗安立／胜义破除／二谛圆融三层。</p>
<p class="small">全书 7.8 万字　·　<a href="{SITE}/book.html">全书阅读版</a>　·　<a href="{SITE}/preface.html">卷首体例</a></p>
{''.join(secs)}
</div></main>""" + foot(), encoding="utf-8")

    # ---- 后记 + 附录 ----
    after = next((b for n, b in rest if n.startswith("后记")), "")
    apps = [(n, b) for n, b in rest if n.startswith("附录")]
    (DOCS / "afterword.html").write_text(
        head(f"后记｜{TITLE}", "一部可以日日使用的经：三十二分读完之后，如何在烦恼起时按图索骥。",
             "/afterword.html", None, act="afterword") +
        f"""<main><div class="wrap">
<p class="eyebrow">后记</p>
<h1>一部可以日日使用的经</h1>
<article>{md2html(after)}</article>
<div class="prevnext"><a href="{SITE}/chapters/">三十二分</a><a href="{SITE}/appendix.html">附录 →</a></div>
</div></main>""" + foot(), encoding="utf-8")

    ach = "".join(f"<h3>{H.escape(n)}</h3>{md2html(b)}" for n, b in apps)
    (DOCS / "appendix.html").write_text(
        head(f"附录｜{TITLE}", "全经科判表、「即非」句式分布、空杯模型对应、底本说明、一页纸金刚经、本自具足篇。",
             "/appendix.html", None, act="afterword") +
        f"""<main><div class="wrap">
<p class="eyebrow">附录 · {len(apps)} 篇</p>
<h1>附录</h1>
<p class="lede">科判与句式分布可作查表用；空杯模型与本自具足篇是三才五蕴太极空杯体系的接口。</p>
<article>{ach}</article>
<div class="prevnext"><a href="{SITE}/afterword.html">← 后记</a><a href="{SITE}/downloads/">下载</a></div>
</div></main>""" + foot(), encoding="utf-8")

    # ---- 首页 ----
    total = sum(r["wc"] for r in recs)
    home_ld = {"@context": "https://schema.org", "@type": "Book", "@id": f"{SITE}/book.html#book",
               "name": TITLE, "alternateName": ["道可道之金刚经", "金刚经通释"],
               "author": {"@type": "Person", "name": "润泽"},
               "inLanguage": "zh-Hans", "version": VER,
               "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
               "description": "《金刚般若波罗蜜经》三十二分通释，以「佛说A—即非A—是名A」三段范式逐分拆解，七段体例，附五篇附录。"}
    if not DOI.endswith("00000000"):
        home_ld["sameAs"] = "https://doi.org/" + DOI
    (DOCS / "index.html").write_text(
        head(TITLE, "《金刚般若波罗蜜经》三十二分通释：原文底本、分题释义、字源名相、逐段深解、俗见勘破、般若范式，一分一页。全书 7.8 万字。",
             "/", home_ld, act="home") +
        f"""<main><div class="wrap">
<p class="eyebrow">{SERIES}</p>
<h1>道可道之金刚经</h1>
<p class="lede">三十二分逐分拆开，只做一件事：把「佛说 A — 即非 A — 是名 A」这把尺子交给读者，让经文自己把般若讲出来。全书约 7.8 万字（{total:,} 字正文）。</p>
<p class="small">v{VER}　·　32 分 + 后记 + 附录五篇　·　CC BY-NC-SA 4.0{('　·　<a href="https://doi.org/%s">DOI %s</a>' % (DOI, DOI)) if not DOI.endswith('00000000') else ''}</p>

<h2>怎么读</h2>
<div class="list">
<div class="row"><div class="no">01</div><div><h3><a href="{SITE}/book.html">全书一页 · 阅读版</a></h3>
<p class="small" style="margin:0;">单文件自包含，无外链、无脚本，断网可读</p></div>
<div class="go"><a href="{SITE}/book.html">打开</a></div></div>
<div class="row"><div class="no">02</div><div><h3><a href="{SITE}/chapters/">三十二分 · 一分一页</a></h3>
<p class="small" style="margin:0;">序分二分、正宗分二十九分、流通分一分，逐分独立成页</p></div>
<div class="go"><a href="{SITE}/chapters/">三十二分</a></div></div>
<div class="row"><div class="no">03</div><div><h3><a href="{SITE}/downloads/">下载 · PDF 与安卓包</a></h3>
<p class="small" style="margin:0;">A5 成书 PDF 与离线 APK，手机断网可读</p></div>
<div class="go"><a href="{SITE}/downloads/">下载</a></div></div>
<div class="row"><div class="no">04</div><div><h3><a href="{SITE}/appendix.html">附录 · 科判与句式分布</a></h3>
<p class="small" style="margin:0;">三十二分脉络表、「即非」句式全经分布、一页纸金刚经</p></div>
<div class="go"><a href="{SITE}/appendix.html">附录</a></div></div>
</div>

<h2>这本书主张什么</h2>
<p>「即非」不是否定，是不执。读成"其实没有这回事"，就滑向断灭空，废因果、废修行、废慈悲——这是本经自己反复警告的坑（"法尚应舍，何况非法"正为此设）。「即非」破的只是"把它当成固定实有的东西抓在手里"，不破它缘起的作用。</p>
<p>正宗分二十九分，须菩提两问（云何应住、云何降伏其心），佛陀一路只答一件事——<b>应无所住而生其心</b>。二十九分，都是在从不同角度拆解"住"这个字。</p>

<h2>体例：一分七段</h2>
<p>原文底本、分题释义、字源与名相、逐段深解、俗见勘破、般若范式与跨典互参、小结。凡「如来说〇〇，即非〇〇，是名〇〇」，单列三层：随俗安立／胜义破除／二谛圆融。底层模型为「三才五蕴太极空杯」，并以老庄、易传、儒门互参。</p>
<p class="small">底本：姚秦鸠摩罗什译；异读随文出注。参考 <a href="{SITE}/preface.html">卷首·体例与总纲</a>。</p>
</div></main>""" + foot(), encoding="utf-8")

    # ---- 下载页 ----
    pdf = next(iter(sorted((ROOT / "book").glob("*.pdf")), ), None)
    apk = next(iter(sorted((ROOT / "packages").glob("**/*.apk")), ), None) if (ROOT / "packages").exists() else None
    pdf_row = ""
    if pdf:
        mb = pdf.stat().st_size / 1e6
        pdf_row = f"""<div class="row"><div class="no">PDF</div><div><h3><a href="{SITE}/downloads/{pdf.name}">{pdf.name.replace('润泽说 道可道之金刚经','成书 PDF')}</a></h3>
<p class="small" style="margin:0;">{mb:.1f} MB，A5 版式，可直接印制</p></div><div class="go"><a href="{SITE}/downloads/{pdf.name}">下载</a></div></div>"""
    apk_row = ""
    if apk:
        mb = apk.stat().st_size / 1e6
        apk_row = f"""<div class="row"><div class="no">APK</div><div><h3><a href="{SITE}/downloads/{apk.name}">安卓离线包 v{VER}</a></h3>
<p class="small" style="margin:0;">{mb:.1f} MB，包名 com.daokedao.jingang，零权限，字体已内置</p></div><div class="go"><a href="{SITE}/downloads/{apk.name}">下载</a></div></div>"""
    (DOCS / "downloads" / "index.html").write_text(
        head(f"下载｜{TITLE}", "《金刚经》通释 A5 成书 PDF 与离线安卓包 APK，零权限、断网可用。",
             "/downloads/", None, act="downloads") +
        f"""<main><div class="wrap">
<p class="eyebrow">下载</p>
<h1>三种拿法</h1>
<p class="lede">要印，取 PDF；要在手机上看，取 APK；要在浏览器里翻，直接用<a href="{SITE}/book.html">全书页</a>。</p>
<div class="list">
{pdf_row}
{apk_row}
<div class="row"><div class="no">MD</div><div><h3><a href="https://github.com/q1z2q3-debug/daokedao-jingang/blob/main/book/润泽说-道可道之金刚经·通释.md">Markdown 母本</a></h3>
<p class="small" style="margin:0;">240 KB，可 diff、可再加工</p></div><div class="go"><a href="https://github.com/q1z2q3-debug/daokedao-jingang/blob/main/book/润泽说-道可道之金刚经·通释.md">GitHub</a></div></div>
<div class="row"><div class="no">HTML</div><div><h3><a href="{SITE}/book.html">单文件阅读版</a></h3>
<p class="small" style="margin:0;">283 KB，无外链、无脚本，可离线转发</p></div><div class="go"><a href="{SITE}/book.html">打开</a></div></div>
</div>
<p class="small">许可：CC BY-NC-SA 4.0。引用请见 CITATION.cff{('　·　DOI <a href="https://doi.org/%s">%s</a>' % (DOI, DOI)) if not DOI.endswith('00000000') else ''}。</p>
</div></main>""" + foot(), encoding="utf-8")

    # ---- 全书页 ----
    (DOCS / "book.html").write_text((BOOK / "金刚经·阅读版.html").read_text(encoding="utf-8"), encoding="utf-8")

    # ---- 机器可读 ----
    (DOCS / "llms.txt").write_text(f"""# {TITLE}

> 润泽（润泽博士）《道可道》系列读本。以「佛说 A — 即非 A — 是名 A」三段范式逐分拆解《金刚般若波罗蜜经》，一分七段，附五篇附录。全书约 7.8 万字。

## 读本
- 全书一页（阅读版，单文件）：{SITE}/book.html
- 三十二分（一分一页）：{SITE}/chapters/
- 卷首·体例与总纲：{SITE}/preface.html
- 后记：{SITE}/afterword.html
- 附录（科判表、即非句式分布、空杯模型、一页纸金刚经）：{SITE}/appendix.html
- 下载（PDF / APK / Markdown 母本）：{SITE}/downloads/
- 仓库：https://github.com/q1z2q3-debug/daokedao-jingang
""" + (f"- DOI：https://doi.org/{DOI}\n" if not DOI.endswith("00000000") else "") + f"""
## 三十二分
""" + "\n".join(f"- 第{r['i']}分 {r['name'][:-1]}：{SITE}/chapters/{r['i']:02d}-{r['slug']}.html（{r['wc']} 字）" for r in recs) + f"""

## 事实
- 底本：姚秦鸠摩罗什译《金刚般若波罗蜜经》，通行字句，异读另注。
- 结构：序分（1–2）、正宗分（3–31）、流通分（32），昭明太子分题，逐分标明「标题非经」。
- 体例：原文底本／分题释义／字源与名相／逐段深解／俗见勘破／般若范式＋跨典互参／小结。
- 关键辨析：「即非」不是否定，是不执；读作「什么都没有」即落断灭空。
- 许可：CC BY-NC-SA 4.0。

## 引用
润泽. {TITLE}：v{VER}. 2026. {('https://doi.org/' + DOI) if not DOI.endswith('00000000') else SITE}
""", encoding="utf-8")

    (DOCS / "robots.txt").write_text("User-agent: *\nAllow: /\n\n" +
                                     "".join(f"User-agent: {b}\nAllow: /\n" for b in
                                             ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot", "Bytespider"]) +
                                     f"\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")

    urls = ["/", "/book.html", "/preface.html", "/chapters/", "/afterword.html", "/appendix.html", "/downloads/"] + \
           [f"/chapters/{r['i']:02d}-{r['slug']}.html" for r in recs]
    (DOCS / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                                      "".join(f"<url><loc>{SITE}{u}</loc><lastmod>2026-11-14</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")

    (DOCS / "favicon.svg").write_text("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" fill="#F7F4EE"/><rect x="6" y="6" width="52" height="52" fill="none" stroke="#944433" stroke-width="2"/>
<text x="32" y="43" text-anchor="middle" font-family="serif" font-size="30" fill="#25211D">金</text></svg>""", encoding="utf-8")

    # 下载页引用的 PDF / APK 同步拷入 docs/downloads
    if pdf:
        (DOCS / "downloads" / pdf.name).write_bytes(pdf.read_bytes())
    if apk:
        (DOCS / "downloads" / apk.name).write_bytes(apk.read_bytes())

    print(f"built {len(list(DOCS.rglob('*.html')))} html pages, {len(recs)} fen, sitemap {len(urls)}")


if __name__ == "__main__":
    build()
