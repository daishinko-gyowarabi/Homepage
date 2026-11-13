# -*- coding: utf-8 -*-
"""インスタにカルーセル投稿する（make_case.py で作った下書きを使う）。

  python3 tools/works/ig_post.py <slug>          準備の確認だけ（画像URLが開けるか・アカウント）
  python3 tools/works/ig_post.py <slug> --yes    投稿する
  python3 tools/works/ig_post.py --check         アカウントとトークンの確認

必要な環境変数（GitHub の Secrets に登録して、Actions から動かす）:
  IG_TOKEN    インスタのアクセストークン（チャットや画面には出さない）
  IG_USER_ID  インスタのユーザーID（Instagram ログインのトークンなら省略可）
  SITE_URL    画像を公開しているサイト（既定 https://homepage.daishinkogyo-warabi.workers.dev）
  IG_API      graph.instagram.com（既定）か graph.facebook.com
画像は main に公開済みのものを使うので、ホームページに反映された後に実行する。
"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DRAFTS = os.path.join(ROOT, 'tools', 'works', 'drafts')
SITE = os.environ.get('SITE_URL', 'https://homepage.daishinkogyo-warabi.workers.dev').rstrip('/')
TOKEN = os.environ.get('IG_TOKEN', '').strip()
# Instagram ログインの鍵は IGAA…、ビジネス（システムユーザー）の鍵は EAA… で始まる
API = 'https://' + (os.environ.get('IG_API') or ('graph.instagram.com' if TOKEN.startswith('IG') else 'graph.facebook.com')) + '/v23.0'
IG_USER_ID = os.environ.get('IG_USER_ID') or '17841464435684827'   # @daishinkogyo.warabi


def call(method, path, **params):
    params['access_token'] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    url = f'{API}/{path}'
    req = urllib.request.Request(url, data=data, method='POST') if method == 'POST' else urllib.request.Request(url + '?' + data.decode())
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'replace')
        sys.exit(f'API エラー {e.code}: {body[:400]}'.replace(TOKEN, '***') if TOKEN else body[:400])


def me():
    uid = 'me' if 'graph.instagram.com' in API else IG_USER_ID
    r = call('GET', uid, fields='id,username')
    print(f"アカウント：@{r.get('username')}（ID {r['id']}）")
    return r['id']


def url_ok(u):
    for _ in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'}), timeout=30) as r:
                if r.status == 200 and r.headers.get('Content-Type', '').startswith('image/jpeg'): return True
        except Exception:
            pass
        time.sleep(5)
    return False


def wait(cid, what):
    for _ in range(40):
        s = call('GET', cid, fields='status_code').get('status_code')
        if s == 'FINISHED': return
        if s in ('ERROR', 'EXPIRED'): sys.exit(f'{what} の処理に失敗しました（{s}）')
        time.sleep(3)
    sys.exit(f'{what} の処理が終わりません')


def main():
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if not TOKEN: sys.exit('IG_TOKEN が設定されていません')
    if a[0] == '--check': me(); return
    slug = a[0]; d = os.path.join(DRAFTS, slug); posted = os.path.join(d, 'posted.json')
    if os.path.exists(posted) and '--again' not in a:
        sys.exit(f"投稿済みです：{json.load(open(posted, encoding='utf-8')).get('permalink')}")
    draft = json.load(open(os.path.join(d, 'insta.json'), encoding='utf-8'))
    urls = [SITE + p for p in draft['images']]
    bad = [u for u in urls if not url_ok(u)]
    if bad: sys.exit('開けない画像があります（ホームページに反映済みか確認）：\n' + '\n'.join(bad))
    print(f'画像 {len(urls)}枚：すべて開けました／投稿文 {len(draft["caption"])}文字')
    uid = me()
    if '--yes' not in a: print('確認だけしました（投稿は --yes）'); return
    if len(urls) == 1:
        c = call('POST', f'{uid}/media', image_url=urls[0], caption=draft['caption'])['id']
    else:
        kids = []
        for i, u in enumerate(urls, 1):
            k = call('POST', f'{uid}/media', image_url=u, is_carousel_item='true')['id']; wait(k, f'{i}枚目'); kids.append(k)
        c = call('POST', f'{uid}/media', media_type='CAROUSEL', children=','.join(kids), caption=draft['caption'])['id']
    wait(c, '投稿')
    mid = call('POST', f'{uid}/media_publish', creation_id=c)['id']
    link = call('GET', mid, fields='permalink').get('permalink')
    json.dump(dict(slug=slug, media_id=mid, permalink=link, posted_at=time.strftime('%Y-%m-%dT%H:%M:%S')),
              open(posted, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'投稿しました：{link}')


if __name__ == '__main__':
    main()
