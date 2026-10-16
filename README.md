# 平野研究室ホームページ

藤田医科大学 医療科学部 臨床教育連携ユニット 診断機器工学分野 平野研究室のウェブサイトです。
内容はすべて `data/` フォルダのテキストファイル（YAML）で管理しており、GitHub 上で編集して保存すると、約1分で自動的にサイトが生成されます（公開設定 `PUBLISH_SITE` が `true` のときは公開サイトへ反映、それ以外は確認用プレビューのみ）。

## 更新のしかた（GitHub のブラウザ画面だけで完結します）

1. GitHub でこのリポジトリを開き、更新したいファイルをクリックします（下の表を参照）。
2. 右上の鉛筆アイコン（Edit this file）を押して編集します。
3. 「Commit changes...」を押して保存します。
4. 「Actions」タブで緑のチェックが付けば完了です（赤い×のときは書式の誤りです。下の「困ったとき」を参照）。

| 更新したい内容 | 編集するファイル | 書き方 |
|---|---|---|
| ニュース | `data/news.yml` | `- date:` から始まる4行を追加（日付順に自動で並ぶので、書く位置はどこでも可） |
| 業績 | `data/publications.yml` | 該当カテゴリの `items:` の直後に `- text:` を追加 |
| メンバー（年度替わり） | `data/members.yml` | 卒業生を `past` へ移し、新メンバーを `current` へ |
| 研究テーマ・共同研究機関 | `data/research.yml` | テーマの説明 `desc` を書くと研究紹介ページに表示 |
| 平野のプロフィール | `data/profile.yml` | 受賞・外部資金などを先頭に追加 |
| 連絡先・カレンダー | `data/site.yml` | `calendar_id` にカレンダーIDを入れると埋め込み表示 |
| 配属・進学希望の方へ | `data/join.yml` | `todo: true` の項目を記入したら、その行を削除 |

各ファイルの先頭に、書き方の例をコメント（`#` で始まる行）で載せています。

### 業績を1件追加する例

```yaml
  - key: journal
    ja: 査読付学術雑誌
    en: Peer-reviewed Journal Articles
    items:
      - text: "Taro Fujita, Harutoyo Hirano. Title of the paper. Journal Name. 2026; 1(2): 3-4"
        url: "https://doi.org/10.xxxx/xxxxx"
      - text: "（既存の論文）..."
```

- 番号は自動で振られます（新しいものが上・番号が大きい）。
- 平野の名前は自動で太字になります。
- 受賞があれば `award: "賞の名前"` の行を足すと、赤枠のバッジで表示されます。

### YAML の注意点

- 字下げ（行頭のスペース）は **半角スペース** で揃えます。タブは使えません。
- 本文に半角の `"` を入れたいときは、全角の “ ” を使ってください。
- `:`（半角コロン）を含む文は、全体を `"` で囲んでください。

## Googleカレンダーを表示する

1. Googleカレンダーで研究室専用のカレンダーを作成します（個人のカレンダーとは分ける）。
2. そのカレンダーの「設定と共有」→「アクセス権限」で「一般公開して誰でも利用できるようにする」をオンにします。
   予定の件名を見せたくない場合は「予定の表示（時間枠のみ、詳細は非表示）」を選びます。
3. 同じ画面の「カレンダーの統合」にある **カレンダーID**（`...@group.calendar.google.com`）をコピーします。
4. `data/site.yml` の `calendar_id: ""` の引用符の中に貼り付けて保存します。

パソコンでは月表示、スマートフォンでは予定一覧で表示されます。

## 「要記入」の表示について

`data/join.yml` で `todo: true` が付いた項目は、確認用プレビューでは黄色の「要記入」付きで表示され、公開時（`PUBLISH_SITE` = `true`）には自動的に非表示になります。

## SNSで共有したときの画像

`static/img/ogp-ja.png`・`ogp-en.png` が共有時に表示されます。研究室名やキャッチコピーを変えたときは `python3 tools/make_ogp.py` で作り直せます（Playwright が必要）。

## 検索エンジンへの登録（公開後・任意）

`sitemap.xml` は自動で作られます。公開後に Google Search Console に公開URLを登録し、`sitemap.xml` を送信すると検索結果に早く反映されます。

## 写真や図を載せる

- `static/img/` に画像をアップロードします（GitHub の「Add file」→「Upload files」）。
- 研究テーマの図：`data/research.yml` の該当テーマに `image: ファイル名.png` を追加。
- 平野の顔写真：`data/profile.yml` の `photo: ""` にファイル名を記入。

## 初回のセットアップ

### ステップ1：非公開で準備・確認する

1. GitHub で研究室用の組織アカウント（Organization、例：`hiranolab`）を作成し、その中に「組織名.github.io」という名前のリポジトリ（例：`hiranolab.github.io`）を **Private** で作成します。
2. このフォルダの中身をすべてアップロードします。
3. この段階ではサイトは公開されません。push（保存）のたびに自動でサイトが生成され、確認用の zip が作られます。

**確認用プレビューの見方**
「Actions」タブ → 一番上の実行結果をクリック → 下の「Artifacts」にある **site-preview** をダウンロード → 解凍して `index.html` をブラウザで開く。
（ダウンロードできるのはリポジトリへのアクセス権がある人だけです）

### ステップ2：確認が終わったら公開する

GitHub Pages は、無料プランでは **Public リポジトリでのみ** 使えます。どちらかを選んでください。

- **無料のまま公開**：Settings → General → Danger Zone → Change visibility で Public にする
  （データファイルや編集履歴も見えるようになります。中身はサイトに載せる内容と同じです）
- **リポジトリは非公開のまま公開**：GitHub Pro（有料）にする。サイト自体は誰でも見られます。

そのうえで：

1. Settings → Pages → Build and deployment の Source を **GitHub Actions** にします。
2. Settings → Secrets and variables → Actions → Variables で、`PUBLISH_SITE` = `true` を追加します。
3. 「Actions」→「Build and deploy」→「Run workflow」を押すと公開されます（`https://<組織名>.github.io/`、このサイトは https://hiranolab.github.io/ ）。
4. 公開URLが決まったら `data/site.yml` の `url:` を書き換えます。
5. （任意）独自ドメインを使う場合は Settings → Pages → Custom domain に設定します。

一時的に公開を止めたいときは、`PUBLISH_SITE` を `false` にしたうえで Settings → Pages の「Unpublish site」を押します。

## 手元で確認する（任意）

Python 3 があれば、次のコマンドで `_site/` にサイトが生成されます。

```sh
pip install pyyaml jinja2
python3 build.py
```

## 困ったとき

- **Actions が赤い×になった**：直前に編集したファイルの字下げや `"` の対応を確認してください。×をクリックするとエラーの行番号が表示されます。
- **「半角カンマがあり、値が途中で切れています」と出た**：`{ ja: ..., en: ... }` の形の行で、値に半角カンマを含むときは、その値を `"` で囲んでください（例：`en: "Graduate School, Shizuoka University"`）。
- **元に戻したい**：ファイルの「History」から以前の版を開き、内容をコピーして貼り戻せます。

## ファイル構成

```
data/          内容（ここだけ編集すれば更新できます）
templates/     ページのレイアウト
static/        CSS・画像
build.py       data と templates から _site/ を生成するスクリプト
.github/       GitHub Actions（自動ビルドと公開）
```
