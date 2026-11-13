# 施工写真 → 施工実績（ホームページ）→ インスタ　の手順

依頼者が Google ドライブの「施工写真」フォルダ（ID `1I3GnlvBjAbclbKnEfcfUst_By0iNVkxi`）に
現場ごとのフォルダを作って写真を入れたら、Claude が次の手順で処理する。
（元にしたスキル：construction-case-pipeline。仕分け・選び方の考え方を引き継ぎ、出力先をこのサイトに合わせたもの）

## 0. 新しい現場を探す
- ドライブの Google Drive コネクタで「施工写真」直下のフォルダを一覧する
- `tools/works/drafts/` に記録がある現場（`source.json` の `drive_folder_id` が一致）は処理済みなので飛ばす
- 写真が4枚未満の現場は飛ばして報告する

## 1. 写真を取ってくる
- 現場フォルダの画像をダウンロードして作業用フォルダ（リポジトリの外。例 `/home/claude/cases/<slug>/photos/`）に保存する
- 現場フォルダに「メモ」（テキストやドキュメント）があれば読む。書式は下の「メモのひな形」
- 元の写真はドライブ上で変更・移動・削除しない

## 2. 写真を選ぶ（全部の写真を自分の目で見てから決める）
- 使うもの：施工前（全景）、主な工程（洗浄・下地補修・下塗り・中塗り・上塗り・防水の各層など）、施工後（全景）
- 工程名は写真の黒板・施工管理アプリの説明欄に**書かれている文字**を根拠にする。ファイル名は根拠にしない。読めなければ推測で書かない（「施工中」とする）
- 使わないもの：人の顔がはっきり写った写真、書類・図面、ピンぼけ、ほぼ同じ写真、黒板が大きく写っているだけの写真
- 表札・車のナンバー・近隣の家の窓や人は `blur` で隠す
- cover（一覧に出す1枚）は施工後の全景。before は同じ向きの施工前があればそれ

## 3. 文章の決まり
- `client` は「市町名 + イニシャル様邸」（例「蕨市 S様邸」）。お客様の実名・番地は書かない
- 地域・イニシャルがフォルダ名・メモ・黒板から分からないときは**作らずに止めて**依頼者に聞く（推測で埋めない）
- 工期・完工時期・塗料名・金額は、メモか黒板に書かれているものだけ使う。分からなければ空欄（金額はメモで「載せてよい」とある場合だけ note に）
- `note` は2〜3文。何をどう直したかを事実だけで書く。「最高品質」「完璧」などの大げさな言葉、他社をけなす言葉は使わない
- `cat` は既存の分類に合わせる：塗装工事 / 防水工事 / リフォーム工事

## 4. 作る
```
python3 tools/works/make_case.py /home/claude/cases/<slug>/case.json --dry   # 構成と投稿文の確認
python3 tools/works/make_case.py /home/claude/cases/<slug>/case.json
```
- `tools/works/drafts/<slug>/source.json` に `{"drive_folder_id": "...", "folder_name": "..."}` を書く（処理済みの印）
- 作業用ブランチ `works/<slug>` に push → プレビューURLで施工実績ページ（PC 1440px・スマホ 390px）を確認
- 依頼者に「プレビューURL」「インスタ画像」「投稿文」を見せる（画像は SendUserFile で送る）

## 5. 公開と投稿（どちらも依頼者のOKが出てから）
- ホームページ：OK が出たら main にマージして push（1〜2分で本番に出る）
- インスタ：本番に出た後、依頼者が投稿をOKしたら GitHub Actions の「インスタ投稿」を実行する
  ```
  gh workflow run instagram.yml -f slug=<slug> -f post=false   # 確認だけ
  gh workflow run instagram.yml -f slug=<slug> -f post=true    # 投稿
  ```
  結果は `gh run watch` で見て、投稿のURLを伝える。二重投稿はツールが止める

## インスタ連携の準備（最初に一度だけ・依頼者と一緒に）
1. インスタのアカウント（@daishinkogyo.warabi）を「プロアカウント（ビジネス）」に切り替える
2. Meta for Developers でアプリを作り、「Instagram API（Instagram ログイン）」を追加してアクセストークンを発行する
3. トークンは**チャットに貼らず**、依頼者自身が GitHub のリポジトリ設定 → Secrets and variables → Actions に
   `IG_TOKEN`（必要なら `IG_USER_ID`）として登録する
4. `gh workflow run instagram.yml -f slug=--check -f post=false` で確認
- 長期トークンは60日で切れる。期限が近づいたら作り直して Secrets を更新する
- 独自ドメインが表示できるようになったら、リポジトリの Variables に `SITE_URL=https://daishinkogyo-warabi.com` を登録する

## メモのひな形（現場フォルダに入れてもらう）
```
町名：
工事内容：（例：外壁塗装・屋根塗装・シーリング打ち替え）
使った塗料：
工期：（例：2026年9月1日〜9月20日）
工事金額：（税込。載せてよい場合だけ）
築年数：
お客様の声：
担当から一言：
```
お客様のお名前は書かない。
