# -*- coding: utf-8 -*-
"""施工写真から「ホームページの施工実績」と「インスタの下書き」を作る。

使い方:
  python3 tools/works/make_case.py <case.json>          作る（works-data.js に追加・写真を書き出し）
  python3 tools/works/make_case.py <case.json> --dry    書き出さずに内容だけ確認

case.json の例（写真のパスは case.json から見た相対パスか絶対パス）:
{
  "slug": "2026-11-warabi-s",            # 英小文字・数字・ハイフン。写真のファイル名になる
  "cat": "塗装工事",                      # 塗装工事 / 防水工事 / リフォーム工事 など
  "client": "蕨市 S様邸",                 # お客様の実名は書かない（イニシャルまで）
  "place": "埼玉県蕨市", "building": "戸建住宅", "work": "外壁塗装・屋根塗装",
  "period": "約2週間", "done": "2026年11月", "note": "",
  "photos": {
    "cover": "photos/after1.jpg",         # 一覧に出す1枚（施工後）
    "before": "photos/before1.jpg",       # ビフォー（無ければ省略）
    "process": [["photos/p1.jpg", "高圧洗浄"], ["photos/p2.jpg", "下塗り"]],
    "after": ["photos/after2.jpg"]
  },
  "blur": {"photos/before1.jpg": [[0.1, 0.7, 0.3, 0.8]]},   # 表札・ナンバー等を隠す範囲（幅・高さに対する割合 x1,y1,x2,y2）
  "caption_extra": ""                     # 投稿文に足したい一言（任意）
}

できるもの:
  public/assets/img/works/<slug>.jpg           一覧・詳細の写真（長辺1600px）
  public/js/works-data.js                      先頭に1件追加（同じ slug があれば何もしない）
  public/assets/img/insta/<slug>/NN.jpg        インスタ用の画像（1080×1350、最大10枚）
  tools/works/drafts/<slug>/caption.txt        投稿文
  tools/works/drafts/<slug>/preview.html       下書きの確認用
  tools/works/drafts/<slug>/insta.json         投稿ツール（ig_post.py）が読む情報
位置情報などの写真の付帯情報は書き出し時に消える。元の写真は変更しない。
"""
import json, os, re, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PUB = os.path.join(ROOT, 'public')
DATA = os.path.join(PUB, 'js', 'works-data.js')
DRAFTS = os.path.join(ROOT, 'tools', 'works', 'drafts')

BRAND = '有限会社大伸工業'
HANDLE = '@daishinkogyo.warabi'
BLUE = (26, 155, 215)          # サイトのブランド色 #1a9bd7
W, H = 1080, 1350
HASHTAGS = ['#大伸工業', '#蕨市', '#埼玉県', '#施工事例', '#ビフォーアフター']
TAGS_BY_WORD = {'外壁': '#外壁塗装', '屋根': '#屋根塗装', '防水': '#防水工事', 'シーリング': '#シーリング',
                'リフォーム': '#リフォーム', '塗装': '#塗装工事'}
FIELDS = ['cat', 'client', 'place', 'building', 'work', 'period', 'done', 'note']

try:
    import pillow_heif; pillow_heif.register_heif_opener()
except ImportError:
    pass


def font(size, weight='Bold'):
    for p in [f'/usr/share/fonts/opentype/noto/NotoSansCJK-{weight}.ttc', 'C:/Windows/Fonts/meiryob.ttc',
              '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc']:
        if os.path.exists(p):
            return ImageFont.truetype(p, size, index=0)
    return ImageFont.load_default()


def load(path, base, blur):
    p = path if os.path.isabs(path) else os.path.join(base, path)
    im = ImageOps.exif_transpose(Image.open(p)).convert('RGB')
    for x1, y1, x2, y2 in blur.get(path, []):
        box = tuple(int(v) for v in (x1 * im.width, y1 * im.height, x2 * im.width, y2 * im.height))
        im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(max(12, im.width // 60))), box)
    return im


def save_jpeg(im, out, long_side=None):
    if long_side:
        im = im.copy(); im.thumbnail((long_side, long_side), Image.LANCZOS)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, 'JPEG', quality=86, optimize=True, progressive=True)   # exif を渡さない＝位置情報は残らない


def fill(im, w, h):
    return ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, 0.5))


def shade(c, top=200, bottom_from=0.66):
    ov = Image.new('L', c.size, 0); d = ImageDraw.Draw(ov)
    for y in range(top):
        d.line([(0, y), (c.width, y)], fill=int(170 * (1 - y / top)))
    y0 = int(c.height * bottom_from)
    for y in range(y0, c.height):
        d.line([(0, y), (c.width, y)], fill=int(220 * (y - y0) / (c.height - y0)))
    c.paste(Image.new('RGB', c.size, (0, 0, 0)), (0, 0), ov)


def wrap(d, text, f, width):
    lines, cur = [], ''
    for ch in text:
        if d.textlength(cur + ch, font=f) > width and cur:
            lines.append(cur); cur = ch
        else:
            cur += ch
    return lines + ([cur] if cur else [])


def label(d, text, x, y, size=34):
    f = font(size); tw = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + tw + 36, y + size + 22], radius=8, fill=BLUE)
    d.text((x + 18, y + (size + 22) / 2), text, font=f, fill='white', anchor='lm')


def footer(d, i, n):
    d.text((48, H - 70), BRAND, font=font(30), fill='white')
    t = f'{i}/{n}'; f = font(28, 'Regular')
    d.text((W - 48 - d.textlength(t, font=f), H - 68), t, font=f, fill='white')


def slide_cover(im, c, n):
    s = fill(im, W, H); shade(s, bottom_from=0.5); d = ImageDraw.Draw(s)
    label(d, c.get('cat') or '施工事例', 48, 56)
    y = H - 400
    d.text((48, y), c['client'], font=font(64), fill='white')
    for line in wrap(d, c['work'], font(44), W - 96)[:2]:
        y += 90; d.text((48, y), line, font=font(44, 'Medium'), fill='white')
    d.text((48, y + 80), c['place'], font=font(32, 'Regular'), fill=(230, 230, 230))
    footer(d, 1, n); return s


def slide_ba(before, after, i, n):
    s = Image.new('RGB', (W, H), 'white'); half = (H - 12) // 2
    s.paste(fill(before, W, half), (0, 0)); s.paste(fill(after, W, half), (0, half + 12))
    d = ImageDraw.Draw(s)
    label(d, 'BEFORE 施工前', 40, 40); label(d, 'AFTER 施工後', 40, half + 52)
    sh = Image.new('L', (W, 110), 0); ImageDraw.Draw(sh).rectangle([0, 0, W, 110], fill=150)
    s.paste(Image.new('RGB', (W, 110), 'black'), (0, H - 110), sh)
    footer(d, i, n); return s


def slide_single(im, title, i, n):
    s = fill(im, W, H); shade(s); d = ImageDraw.Draw(s)
    label(d, title, 48, 56); footer(d, i, n); return s


def caption(c):
    tags = list(dict.fromkeys([t for k, t in TAGS_BY_WORD.items() if k in c['work'] + c.get('cat', '')] + HASHTAGS))
    rows = [f"【施工事例】{c['client']}", '', f"工事内容：{c['work']}"]
    for k, v in [('施工場所', c.get('place')), ('建物', c.get('building')), ('工期', c.get('period')), ('完工', c.get('done'))]:
        if v: rows.append(f'{k}：{v}')
    if c.get('note'): rows += ['', c['note']]
    if c.get('caption_extra'): rows += ['', c['caption_extra']]
    rows += ['', '塗装・防水・リフォームのご相談は', 'プロフィールのホームページから、またはお電話で。',
             '☎ 048-431-2045', '', f'{BRAND}（埼玉県蕨市）', '', ' '.join(tags)]
    return '\n'.join(rows)


def js_str(v):
    return json.dumps(v or '', ensure_ascii=False)


def add_to_data(c, img):
    src = open(DATA, encoding='utf-8').read()
    if f'/works/{c["slug"]}.jpg' in src:
        print('works-data.js：同じ事例がすでにあるので追加しません'); return False
    entry = ('  {\n'
             f'    cat: {js_str(c.get("cat"))}, client: {js_str(c["client"])},\n'
             f'    place: {js_str(c.get("place"))}, building: {js_str(c.get("building"))}, work: {js_str(c["work"])},\n'
             f'    period: {js_str(c.get("period"))}, done: {js_str(c.get("done"))}, note: {js_str(c.get("note"))},\n'
             f'    img: {js_str(img)}\n'
             '  },\n')
    if re.search(r'^window\.WORKS = \[\];', src, re.M):
        src = re.sub(r'^// 現在は施工実績を掲載していません.*\n', '', src, flags=re.M)
        src = re.sub(r'^window\.WORKS = \[\];', 'window.WORKS = [\n' + entry + '];', src, flags=re.M)
    else:
        src = re.sub(r'^window\.WORKS = \[\n', lambda m: m.group(0) + entry, src, count=1, flags=re.M)
    open(DATA, 'w', encoding='utf-8').write(src); return True


def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    path = os.path.abspath(sys.argv[1]); dry = '--dry' in sys.argv
    c = json.load(open(path, encoding='utf-8')); base = os.path.dirname(path)
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{2,60}', c.get('slug', '')): sys.exit('slug は英小文字・数字・ハイフンで書いてください')
    for k in ['client', 'work', 'photos']:
        if not c.get(k): sys.exit(f'{k} が空です')
    if re.search(r'[一-龥ぁ-んァ-ン]{2,}様', c['client']): sys.exit('client にお客様の実名が入っていないか確認してください（「S様邸」のようにイニシャルで）')
    ph, blur = c['photos'], c.get('blur', {})
    get = lambda p: load(p, base, blur)

    cover = get(ph['cover'])
    slides = [('表紙', lambda n: slide_cover(cover, c, n))]
    if ph.get('before'):
        b = get(ph['before']); slides.append(('ビフォーアフター', lambda n, i=len(slides) + 1: slide_ba(b, cover, i, n)))
    for p, t in ph.get('process', []):
        if len(slides) >= 9: break
        im = get(p); slides.append((t, lambda n, i=len(slides) + 1, im=im, t=t: slide_single(im, t, i, n)))
    for p in ph.get('after', []):
        if len(slides) >= 10: break
        im = get(p); slides.append(('施工完了', lambda n, i=len(slides) + 1, im=im: slide_single(im, '施工完了', i, n)))
    n = len(slides); text = caption(c)
    print(f"事例：{c['client']}（{c['work']}）／インスタ画像 {n}枚／投稿文 {len(text)}文字")
    print('構成：' + ' → '.join(t for t, _ in slides))
    if dry: print('\n--- 投稿文 ---\n' + text); return

    img = f'/assets/img/works/{c["slug"]}.jpg'
    save_jpeg(cover, os.path.join(PUB, img.lstrip('/')), 1600)
    added = add_to_data(c, img)
    idir = os.path.join(PUB, 'assets', 'img', 'insta', c['slug']); ddir = os.path.join(DRAFTS, c['slug'])
    files = []
    for k, (t, make) in enumerate(slides, 1):
        f = f'{k:02d}.jpg'; save_jpeg(make(n), os.path.join(idir, f)); files.append(f)
    os.makedirs(ddir, exist_ok=True)
    open(os.path.join(ddir, 'caption.txt'), 'w', encoding='utf-8').write(text)
    json.dump(dict(slug=c['slug'], images=[f'/assets/img/insta/{c["slug"]}/{f}' for f in files], caption=text),
              open(os.path.join(ddir, 'insta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    imgs = ''.join(f'<img src="../../../../public/assets/img/insta/{c["slug"]}/{f}">' for f in files)
    open(os.path.join(ddir, 'preview.html'), 'w', encoding='utf-8').write(
        '<!doctype html><meta charset="utf-8"><title>インスタ下書き</title><style>body{font-family:sans-serif;margin:20px}'
        'img{width:270px;margin:4px;border:1px solid #ccc}pre{white-space:pre-wrap;background:#f5f5f5;padding:12px;max-width:600px}</style>'
        f'<h1>{c["client"]}</h1>{imgs}<pre>{text}</pre>')
    print(f'書き出し：{img}' + ('（works-data.js に追加）' if added else ''))
    print(f'インスタ下書き：tools/works/drafts/{c["slug"]}/')


if __name__ == '__main__':
    main()
