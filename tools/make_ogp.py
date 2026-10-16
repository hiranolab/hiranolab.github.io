#!/usr/bin/env python3
"""SNS・チャットで共有したときに表示される画像（static/img/ogp-ja.png, ogp-en.png）を作り直すスクリプト。
研究室名やキャッチコピーを変えたときだけ実行します（Playwright と日本語フォントが必要）。
  pip install playwright pyyaml && playwright install chromium
  python3 tools/make_ogp.py
"""
from pathlib import Path
import sys
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import pulse_path  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
site = yaml.safe_load(open(ROOT / "data/site.yml", encoding="utf-8"))
import base64  # noqa: E402
LOGO = base64.b64encode((ROOT / "static/img/logo.svg").read_bytes()).decode()

HTML = """<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><style>
body{{margin:0;width:1200px;height:630px;background-color:#0b1720;background-image:linear-gradient(rgba(79,210,234,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(79,210,234,.08) 1px,transparent 1px);background-size:60px 60px;color:#fff;
 font-family:"BIZ UDPGothic","Noto Sans CJK JP","Noto Sans JP",sans-serif;position:relative;overflow:hidden}}
.aff{{position:absolute;left:80px;top:78px;font-family:"BIZ UDPGothic","Noto Sans CJK JP",sans-serif;font-size:{affsize}px;color:#93a9b8;width:860px;line-height:1.5}}
.logo{{position:absolute;right:72px;top:64px;width:150px;height:150px}}
h1{{position:absolute;left:76px;top:150px;margin:0;font-size:{h1}px;letter-spacing:{ls};font-weight:700}}
.tag{{position:absolute;left:80px;top:{tagtop}px;font-size:{tagsize}px;width:1060px;line-height:1.55;font-weight:700;color:#e7eff4}}
svg{{position:absolute;left:0;bottom:40px;width:1200px;height:120px}}
.bar{{display:none}}
</style></head><body><div class="bar"></div>
<img class="logo" src="data:image/svg+xml;base64,{logo}"><div class="aff">{aff}</div><h1>{lab}</h1><div class="tag">{tag}</div>
<svg viewBox="0 0 1200 90" preserveAspectRatio="xMinYMid slice"><path d="M0,86 H1200" stroke="#21384a" fill="none"/>
<path d="{pulse}" stroke="#ff4b61" stroke-width="3" style="filter:drop-shadow(0 0 6px rgba(255,75,97,.6))" fill="none" stroke-linejoin="round"/></svg></body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1200, "height": 630})
    for lang in ["ja", "en"]:
        pg.set_content(HTML.format(
            lang=lang, aff=site["affiliation"][lang], lab=site["lab"][lang], tag=site["tagline"][lang],
            logo=LOGO, affsize=26 if lang == "ja" else 21, pulse=pulse_path(), h1=120 if lang == "ja" else 104, ls=".12em" if lang == "ja" else "0",
            tagtop=330 if lang == "ja" else 320, tagsize=30 if lang == "ja" else 32))
        pg.screenshot(path=str(ROOT / f"static/img/ogp-{lang}.png"))
    b.close()
print("wrote static/img/ogp-ja.png, ogp-en.png")
