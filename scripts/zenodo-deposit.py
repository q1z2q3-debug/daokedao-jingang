#!/usr/bin/env python3
"""把《金刚经》存入 Zenodo，取一个可引用的 DOI。

用法：
  export ZENODO_TOKEN=$(~/.daokedao-vault/cred zenodo)
  python3 scripts/zenodo-deposit.py --dry-run      # 建草稿、传附件，不发布
  python3 scripts/zenodo-deposit.py --publish      # DOI 立即生效，不可撤销
"""
import argparse, json, os, time, urllib.error, urllib.request
from pathlib import Path

BASE = "https://zenodo.org/api"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
ROOT = Path(__file__).resolve().parent.parent
VER = "1.0.2"
DOI_LOCKED = "10.5281/zenodo.24222027"

FILES = [
    ("book/润泽说-道可道之金刚经·通释.md", "daokedao-jingang-v1.0.2.md"),
    ("book/润泽说 道可道之金刚经.pdf", "daokedao-jingang-v1.0.2.pdf"),
    ("book/金刚经·阅读版.html", "daokedao-jingang-reader-v1.0.2.html"),
    ("packages/apk-1.0.2-jingang/道可道-金刚经-1.0.2.apk", "daokedao-jingang-reader-v1.0.2.apk"),
]
META = {"metadata": {
    "title": "润泽说 道可道之金刚经（v1.0.2）",
    "upload_type": "publication",
    "publication_type": "book",
    "publication_date": "2026-11-14",
    "version": VER,
    "language": "zho",
    "license": "cc-by-nc-sa-4.0",
    "creators": [{"name": "润泽"}],
    "keywords": ["金刚经", "般若", "佛教", "三十二分", "即非", "中国哲学", "鸠摩罗什"],
    "description": (
        "<p>《金刚般若波罗蜜经》三十二分通释。全书约 7.8 万字（83,380 字），"
        "32 分正文，另附后记与五篇附录。</p>"
        "<p>体例：每分七段——原文底本、分题释义、字源与名相、逐段深解、俗见勘破、"
        "般若范式与跨典互参、小结。凡「如来说〇〇，即非〇〇，是名〇〇」句式，"
        "单列三层：随俗安立（佛说 A）／胜义破除（即非 A）／二谛圆融（是名 A）。</p>"
        "<p>立宗：「即非」不是否定，是不执；读作「其实没有这回事」即落断灭空。"
        "正宗分二十九分只答一事——应无所住而生其心。底层模型为「三才五蕴太极空杯」，"
        "并以老庄、易传、儒门互参。</p>"
        "<p>附件：Markdown 母本、A5 成书 PDF（182 页）、单文件 HTML 阅读版、"
        "安卓离线包（零权限、断网可用、字体内置）。</p>"
    ),
    "related_identifiers": [
        {"relation": "isSupplementTo",
         "identifier": "https://github.com/q1z2q3-debug/daokedao-jingang",
         "resource_type": "software"},
        {"relation": "isAlternateIdentifier",
         "identifier": "https://q1z2q3-debug.github.io/daokedao-jingang/",
         "resource_type": "other"},
        {"relation": "isPartOf",
         "identifier": "https://q1z2q3-debug.github.io/runze-daokedao/",
         "resource_type": "other"},
    ],
    "notes": "许可 CC BY-NC-SA 4.0。引用请注明书名与版本号 v1.0.2。本书为「润泽说 道可道」系列般若系读本，与《心经通释》互参。",
}}


def call(url, token, data=None, method="POST", raw=None, tries=6):
    """Zenodo 偶发 503，按退避重试。"""
    body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
    last = None
    for i in range(tries):
        req = urllib.request.Request(url, data=body, method=method, headers={
            "Authorization": f"Bearer {token}", "User-Agent": UA,
            "Content-Type": "application/json", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504):
                print(f"  zenodo {e.code}，{30*(i+1)}s 后重试（{i+1}/{tries}）")
                time.sleep(30 * (i + 1))
                continue
            raise
    raise last


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--publish", action="store_true")
    a = ap.parse_args()
    token = os.environ.get("ZENODO_TOKEN") or ""
    if not token:
        raise SystemExit("缺 ZENODO_TOKEN")

    dep = call(BASE + "/deposit/depositions", token, {})
    dep_id = dep["id"]
    bucket = dep["links"]["bucket"]
    print("draft", dep_id, dep["links"]["html"])

    call(BASE + f"/deposit/depositions/{dep_id}", token, META, method="PUT")

    for path, name in FILES:
        data = (ROOT / path).read_bytes()
        for i in range(6):
            req = urllib.request.Request(f"{bucket}/{name}", data=data, method="PUT", headers={
                "Authorization": f"Bearer {token}", "User-Agent": UA,
                "Content-Type": "application/octet-stream"})
            try:
                with urllib.request.urlopen(req, timeout=900) as r:
                    j = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and i < 5:
                    print(f"  up {e.code}，{30*(i+1)}s 后重试")
                    time.sleep(30 * (i + 1))
                    continue
                raise
        print("  up", j.get("key"), j.get("size"))

    if a.publish:
        pub = call(BASE + f"/deposit/depositions/{dep_id}/actions/publish", token, {}, method="POST")
        print("DOI", pub.get("doi"), pub.get("links", {}).get("doi"))
    else:
        print("草稿未发布：", dep["links"]["html"])


if __name__ == "__main__":
    main()
