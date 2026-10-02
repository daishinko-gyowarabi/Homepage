# 有限会社大伸工業 ホームページ

https://daishinkogyo-warabi.com/

HTML・CSS・JavaScript だけで作った静的サイトです。サイト本体は `public` フォルダに入っています。
GitHub の `main` ブランチを更新すると、Cloudflare（Workers）が自動でサイトに反映します（1〜2分）。
設定は `wrangler.jsonc` にあります。

## ファイル構成（`public` フォルダの中）

| ファイル | 内容 |
|---|---|
| `index.html` | トップページ |
| `business.html` | 事業内容 |
| `works.html` | 施工実績（事例のデータは `js/works-data.js`） |
| `recruit.html` | 採用情報・応募フォーム |
| `company.html` | 会社案内 |
| `contact.html` | お問い合わせフォーム |
| `404.html` | ページが見つからないときの画面 |
| `css/style.css` | 全ページ共通のデザイン |
| `js/main.js` | 写真の切り替え・メニューなどの動き |
| `js/form.js` / `js/form-config.js` | フォームの確認画面・送信と、その設定 |
| `assets/img/` | 画像（施工実績の写真は `assets/img/works/`） |
| `sitemap.xml` / `robots.txt` | 検索エンジン向けの設定 |
| `_headers` / `_redirects` | Cloudflare 用の設定（キャッシュ、www なしへの転送） |

## よくある更新

### 施工実績を追加する
1. 写真を `public/assets/img/works/` に入れる（例：`work-05.jpg`。横長・幅1600px程度がおすすめ）
2. `public/js/works-data.js` に事例を1件追加し、`img` に `/assets/img/works/work-05.jpg` と書く
3. 保存して GitHub に反映

`cat`（分類）に「塗装工事」「防水工事」などを入れると、一覧の上に絞り込みボタンが自動で出ます。

### 電話番号・FAX を変える
全ページに入っています。エディタの「すべてのファイルを検索して置換」で
`048-000-0000`（表示用）と `tel:0480000000`（電話リンク用）を置き換えてください。

### 文章を変える
各ページの `.html` を開き、該当する文章を直接書き換えます。

## フォームの送信設定

フォームの内容は [Web3Forms](https://web3forms.com)（無料・月250件まで）経由でメールに届きます。

1. https://web3forms.com を開き、受信したいメールアドレスを入力して Access Key を受け取る
2. `public/js/form-config.js` の `accessKey: ""` の `""` の中にキーを貼り付ける
3. GitHub に反映

キーが未設定の間は、送信ボタンを押すと「お電話でお問い合わせください」と案内が出ます。

## 手元で確認する

```bash
npx wrangler dev
```
