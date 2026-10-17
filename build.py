#!/usr/bin/env python3
"""平野研究室サイトのビルドスクリプト

data/*.yml と templates/*.html から _site/ に静的サイトを生成します。
  python3 build.py            # _site/ に出力
GitHub に push すると .github/workflows/deploy.yml が自動で実行し、公開まで行います。
"""
import datetime
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
LANGS = ["ja", "en"]
# 公開ビルドかどうか（GitHub Actions で PUBLISH_SITE=true のとき）。公開時は「要記入」の項目を出さない
PUBLISH = os.environ.get("PUBLISH_SITE", "").lower() == "true"

PAGES = [
    # (slug, template, nav label key or None)
    ("index", "index.html", None),
    ("research", "research.html", "research"),
    ("members", "members.html", "members"),
    ("hirano", "hirano.html", None),
    ("publications", "publications.html", "publications"),
    ("news", "news.html", "news"),
    ("schedule", "schedule.html", "schedule"),
    ("join", "join.html", "join"),
    ("contact", "contact.html", "contact"),
    ("404", "404.html", None),
]

T = {
    "home": {"ja": "ホーム", "en": "Home"},
    "research": {"ja": "研究紹介", "en": "Research"},
    "members": {"ja": "メンバー", "en": "Members"},
    "publications": {"ja": "業績", "en": "Publications"},
    "news": {"ja": "ニュース", "en": "News"},
    "schedule": {"ja": "スケジュール", "en": "Schedule"},
    "contact": {"ja": "連絡先", "en": "Contact"},
    "join": {"ja": "配属・進学希望の方へ", "en": "Prospective students"},
    "key_papers": {"ja": "代表的な論文", "en": "Key papers"},
    "trace_label": {"ja": "動脈圧波形", "en": "Arterial pressure"},
    "cta_research": {"ja": "研究を見る", "en": "Explore our research"},
    "todo": {"ja": "要記入", "en": "To be completed"},
    "nf_title": {"ja": "ページが見つかりません", "en": "Page not found"},
    "nf_body": {"ja": "お探しのページは移動したか，削除された可能性があります．上のメニューから目的のページを選んでください．", "en": "The page you are looking for may have moved or been removed. Please choose a page from the menu above."},
    "nf_home": {"ja": "トップページへ", "en": "Go to the home page"},
    "hirano": {"ja": "平野 陽豊", "en": "Harutoyo Hirano"},
    "switch": {"ja": "English", "en": "日本語"},
    "menu": {"ja": "メニュー", "en": "Menu"},
    "skip": {"ja": "本文へ移動", "en": "Skip to content"},
    "themes": {"ja": "研究テーマ", "en": "Research topics"},
    "all_news": {"ja": "すべてのニュース", "en": "All news"},
    "more_research": {"ja": "研究紹介を見る", "en": "About our research"},
    "collaborators": {"ja": "共同研究機関", "en": "Collaborators"},
    "collab_lead": {
        "ja": "これまでに以下の外部共同研究機関や多くの研究協力者によって支えられてきました．",
        "en": "Our work has been supported by the following partner institutions and many collaborators.",
    },
    "faculty": {"ja": "教員", "en": "Faculty"},
    "students": {"ja": "学生", "en": "Students"},
    "past_members": {"ja": "過去のメンバー", "en": "Former members"},
    "profile": {"ja": "プロフィール", "en": "Profile"},
    "career": {"ja": "略歴", "en": "Career"},
    "theses": {"ja": "学位論文", "en": "Theses"},
    "societies": {"ja": "所属学会", "en": "Memberships"},
    "awards": {"ja": "受賞", "en": "Awards"},
    "grants": {"ja": "獲得外部資金", "en": "Research grants"},
    "projects": {"ja": "共同研究プロジェクト", "en": "Collaborative projects"},
    "service": {"ja": "学会・社会活動", "en": "Professional service"},
    "international": {"ja": "国際連携", "en": "International partnerships"},
    "teaching": {"ja": "担当講義", "en": "Teaching"},
    "pub_all": {"ja": "すべて", "en": "All"},
    "pub_search": {"ja": "著者名・キーワードで絞り込む", "en": "Filter by author or keyword"},
    "pub_count": {"ja": "件", "en": " items"},
    "pub_none": {"ja": "条件に合う業績はありません．キーワードを変えてみてください．", "en": "No items match. Try a different keyword."},
    "link": {"ja": "リンク", "en": "Link"},
    "cal_empty": {
        "ja": "スケジュールは準備中です．",
        "en": "The schedule will be available soon.",
    },
    "phone": {"ja": "電話", "en": "Phone"},
    "email": {"ja": "メール", "en": "Email"},
    "mail_note": {"ja": "迷惑メール対策のため，[at_m] を @ に置き換えて送信してください．", "en": "To prevent spam, please replace [at_m] with @."},
    "cal_open": {"ja": "Googleカレンダーで開く", "en": "Open in Google Calendar"},
    "office": {"ja": "居室", "en": "Office"},
    "address": {"ja": "所在地", "en": "Address"},
    "prospective": {
        "ja": "研究室への配属や大学院進学，共同研究のご相談は，メールでお気軽にご連絡ください．",
        "en": "For enquiries about joining the lab, graduate study or collaboration, please contact us by email.",
    },
    "updated": {"ja": "最終更新", "en": "Last updated"},
}

NAME_RE = re.compile(r"(Harutoyo Hirano|平野\s?陽豊)")


def t(key, lang):
    return T[key][lang]


def pick(v, lang):
    """{ja:..., en:...} から言語に合う方を返す（英語が空なら日本語）"""
    if isinstance(v, dict):
        return v.get(lang) or v.get("ja") or ""
    return v or ""


def emph_name(text):
    s = html.escape(text, quote=False)
    return Markup(NAME_RE.sub(r"<strong>\1</strong>", s))


def fmt_date(d, lang):
    if isinstance(d, str):
        d = datetime.date.fromisoformat(d)
    if lang == "ja":
        return f"{d.year}年{d.month}月{d.day}日"
    return d.strftime("%-d %b %Y")


def abp_wave(u):
    """1拍 (0..1) の動脈圧波形（トップの canvas と同じ式）"""
    import math
    def g(x, m, sd):
        return math.exp(-((x - m) ** 2) / (2 * sd * sd))
    def w0(x):
        rise = 1 / (1 + math.exp(-(x - 0.07) / 0.012))
        return rise * (0.85 * g(x, .17, .075) + .38 * g(x, .31, .07) + .24 * g(x, .47, .045)
                       + .30 * math.exp(-(x - 0.2) / 0.55))
    rise = 1 / (1 + math.exp(-(u - 0.07) / 0.012))
    return w0(u) + w0(1) * (1 - rise)


def pulse_path(beats=6, width=200, top=12, bottom=86, samples=80):
    """動脈圧波形の SVG パス（各ページ見出し・共有画像で使用）"""
    vals = [abp_wave(k / samples) for k in range(samples)]
    vmax = max(vals)
    pts = []
    for b in range(beats):
        for k, v in enumerate(vals):
            x = b * width + k * width / samples
            y = bottom - v / vmax * (bottom - top)
            pts.append(f"{x:.1f},{y:.1f}")
    return "M" + " L".join(pts)


def load(name):
    path = ROOT / "data" / f"{name}.yml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    check_values(data, f"data/{name}.yml")
    return data


def check_values(x, where):
    """{ ja: ..., en: ... } の中に半角カンマを含む値を引用符なしで書くと、値が途中で切れる。
    その書き損じを見つけたらビルドを止めて場所を知らせる。"""
    if isinstance(x, dict):
        for k, v in x.items():
            if v is None:
                sys.exit(f"[エラー] {where}: 「{k}」の前に半角カンマがあり、値が途中で切れています。"
                         f"その値全体を \" \" で囲んでください。（{x}）")
            check_values(v, where)
    elif isinstance(x, list):
        for v in x:
            check_values(v, where)


def last_updated():
    """内容（data / templates / static）を最後に変更したコミットの日付。git がなければ今日。"""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", "data", "templates", "static"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        if out:
            return datetime.date.fromisoformat(out)
    except Exception:
        pass
    return datetime.date.today()


def main():
    data = {n: load(n) for n in ["site", "news", "members", "research", "publications", "profile", "join"]}
    # ニュースは書いた順に関係なく新しい順に並べる（同じ日付は書いた順のまま）
    data["news"] = sorted(data["news"], key=lambda n: str(n["date"]), reverse=True)
    pub_total = sum(len(c["items"]) for c in data["publications"]["categories"])
    today = datetime.date.today()
    updated = last_updated()

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["emph"] = emph_name
    # CSS・画像を更新したときにブラウザの古いキャッシュを使わせないための印（中身から計算）
    import hashlib
    h = hashlib.sha1()
    for f in sorted((ROOT / "static").rglob("*")):
        if f.is_file():
            h.update(f.read_bytes())
    env.globals["v"] = h.hexdigest()[:8]

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "en").mkdir(parents=True)
    shutil.copytree(ROOT / "static", OUT / "static")
    # root/ のファイルはサイトの一番上にそのまま置く（Google Search Console の確認用ファイルなど）
    if (ROOT / "root").is_dir():
        for f in (ROOT / "root").iterdir():
            if f.is_file():
                shutil.copy2(f, OUT / f.name)

    nav = [(slug, key) for slug, _, key in PAGES if key]

    for lang in LANGS:
        root = "" if lang == "ja" else "../"
        other_root = "en/" if lang == "ja" else "../"
        for slug, tpl, _ in PAGES:
            # 404 ページはどの階層からも表示されるので，リンクを公開URLからの絶対パスにする
            if slug == "404":
                base_url = data["site"]["url"]
                page_root, nav_root, switch = base_url, base_url, f"{base_url}en/index.html"
            else:
                page_root, nav_root, switch = root, "", f"{other_root}{slug}.html"
            ctx = dict(
                lang=lang,
                root=page_root,
                navroot=nav_root,
                here=f"{slug}.html",
                switch_href=switch,
                slug=slug,
                nav=nav,
                t=lambda k, _l=lang: t(k, _l),
                p=lambda v, _l=lang: pick(v, _l),
                d=lambda v, _l=lang: fmt_date(v, _l),
                pub_total=pub_total,
                pulse=pulse_path(),
                publish=PUBLISH,
                today=today,
                updated=updated,
                **data,
            )
            out_dir = OUT if lang == "ja" else OUT / "en"
            (out_dir / f"{slug}.html").write_text(env.get_template(tpl).render(**ctx), encoding="utf-8")

    base = data["site"]["url"]
    urls = []
    for lang in LANGS:
        for slug, _, _ in PAGES:
            if slug == "404":
                continue
            urls.append(f"{base}{'' if lang == 'ja' else 'en/'}{slug}.html")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{updated.isoformat()}</lastmod></url>\n" for u in urls)
        + "</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}sitemap.xml\n", encoding="utf-8")
    (OUT / "en" / "404.html").unlink()

    print(f"built {len(PAGES) * len(LANGS) - 1} pages, {pub_total} publications -> {OUT}")


if __name__ == "__main__":
    main()
