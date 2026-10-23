"""siberpy.github.io statik site üreticisi. Kaynak: kaynaklar/*.md (depoda). Çıktı: <out>/index.html + <out>/<anchor>/index.html
Kullanım: python3 build_site.py <kaynaklar_klasörü> <çıktı_klasörü>"""
import sys, re, glob, os, html, markdown, shutil
KW = {"yol": "YOL", "prompt": "PROMPT", "hazine": "HAZİNE", "liste": "LİSTE", "cevap": "CEVAP", "repo": "REPO"}
src, out = sys.argv[1], sys.argv[2]
tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site_sablon.html"), encoding="utf-8").read()
os.makedirs(out, exist_ok=True)

def linkify(h):
    return re.sub(r'(?<!["\'>=])(https?://[^\s<)]+[^\s<).,;:])', r'<a href="\1" target="_blank" rel="noopener">\1</a>', h)

def page(title, desc, body, path):
    p = tpl.replace("{{TITLE}}", html.escape(title)).replace("{{DESC}}", html.escape(desc)).replace("{{BODY}}", body)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(p)

files = sorted([f for f in glob.glob(os.path.join(src, "*.md")) if not f.endswith("README.md")], reverse=True)
items, seen = [], set()
for f in files:
    base = os.path.basename(f)[:-3]
    date, slug = base[:10], base[11:]
    y, m, d = date.split("-")
    key = slug.split("-")[0]
    kw = KW.get(key)
    anchor = key if kw else slug
    if anchor in seen:  # aynı kelime ikinci kez kullanıldıysa tarihli adres
        anchor = f"{anchor}-{y}{m}{d}"
    seen.add(anchor)
    raw = open(f, encoding="utf-8").read()
    raw = re.sub(r"\n*\[@siber\.py\]\(https://www\.instagram\.com/siber\.py/\)[^\n]*\n*$", "\n", raw).rstrip()
    raw = re.sub(r"^.*Takip et: \[@siber\.py\].*$", "", raw, flags=re.M)
    raw = re.sub(r"^.*\[@siber\.py\]\(https://www\.instagram\.com/siber\.py/\).*$", "", raw, flags=re.M)
    lines = raw.split("\n")
    title = lines[0].lstrip("# ").strip()
    hb = markdown.markdown("\n".join(lines[1:]), extensions=["fenced_code", "tables", "sane_lists"])
    hb = linkify(hb)
    hb = re.sub(r"<pre><code>(.*?)</code></pre>", lambda mm: '<div class="code"><pre><code>' + mm.group(1) + '</code></pre><button class="copy" type="button">Kopyala</button></div>', hb, flags=re.S)
    tag = f'<span class="kw">{kw}</span>' if kw else '<span class="kw alt">UYARI</span>'
    first_p = re.sub("<[^>]+>", "", (re.search(r"<p>(.*?)</p>", hb, re.S) or re.search(r"<li>(.*?)</li>", hb, re.S)).group(1))[:150]
    art = f'''<a class="back" href="/">← Tüm dosyalar</a>
<article><p class="meta"><span class="date">{d}.{m}.{y}</span>{tag}</p><h1>{html.escape(title)}</h1><div class="body">{hb}</div></article>'''
    page(f"{title} · siber.py", first_p, art, os.path.join(out, anchor, "index.html"))
    items.append(f'<li><a class="row" href="/{anchor}/"><span class="date">{d}.{m}.{y}</span>{tag}<span class="t">{html.escape(title)}</span></a></li>')

idx = f'''<h1>Videodaki <mark>linkler</mark> burada.</h1>
<p class="lead">@siber.py Reel'lerinde "yorumlara yaz" dediğimiz her bölümün kaynakları, komutları ve resmî linkleri. Yapay zeka, yazılım ve siber güvenlik; sade Türkçe. En yeni üstte.</p>
<ul class="list">{"".join(items)}</ul>'''
page("siber.py Kaynaklar", "Yapay zeka, yazılım ve siber güvenlik: @siber.py Reel'lerindeki kaynaklar, komutlar ve resmî linkler.", idx, os.path.join(out, "index.html"))
open(os.path.join(out, ".nojekyll"), "w").close()
print("ok", len(items))
