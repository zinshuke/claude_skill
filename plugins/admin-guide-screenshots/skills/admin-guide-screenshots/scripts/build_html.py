#!/usr/bin/env python3
"""Build HTML pages from the admin guides' local Markdown copies.

Usage:
    python3 build_html.py [GUIDES_DIR] [--guide NAME ...] [--embed]

GUIDES_DIR defaults to docs/admin-guides. For each <guide>/ folder with a guide.json and a
<guide>-admin-guide.md, writes <guide>/index.html (images linked from img/). Also writes
GUIDES_DIR/index.html listing every guide.

--embed  inline the screenshots as data URIs, so a guide page is one file you can email or
         attach (larger: a few MB per guide).
--zip [FILE]  also pack the index page, the guide pages and the screenshots they use into a zip
         (default docs/admin-guides-html-<date>.zip). Working files are left out.

Needs: pip install markdown
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
	import markdown
except ImportError:
	sys.exit("Python-Markdown is missing: pip install markdown")

ACCENT = "#e5262f"

CSS = """
:root{--bg:#f6f7f9;--panel:#fff;--text:#1d2330;--muted:#5d6675;--line:#dfe3ea;--accent:%(accent)s;
--accent-soft:#fdecec;--code:#eef1f5;--shadow:0 1px 3px rgba(16,24,40,.08),0 4px 16px rgba(16,24,40,.06)}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#11141a;--panel:#191d25;--text:#e6e9ef;
--muted:#9aa3b2;--line:#2a303b;--accent-soft:#3a1d20;--code:#232833;--shadow:0 1px 3px rgba(0,0,0,.4)}}
:root[data-theme=dark]{--bg:#11141a;--panel:#191d25;--text:#e6e9ef;--muted:#9aa3b2;--line:#2a303b;
--accent-soft:#3a1d20;--code:#232833;--shadow:0 1px 3px rgba(0,0,0,.4)}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:16px}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--accent)}
.layout{display:grid;grid-template-columns:280px minmax(0,1fr);max-width:1320px;margin:0 auto;gap:32px;padding:24px 16px}
nav.toc{position:sticky;top:16px;align-self:start;max-height:calc(100vh - 32px);overflow:auto;background:var(--panel);
border:1px solid var(--line);border-radius:12px;padding:16px;box-shadow:var(--shadow)}
nav.toc .back{display:block;font-size:13px;color:var(--muted);text-decoration:none;margin-bottom:8px}
nav.toc h2{font-size:15px;margin:0 0 10px}
nav.toc input{width:100%%;padding:7px 10px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--text);margin-bottom:10px}
nav.toc ol{list-style:none;margin:0;padding:0;counter-reset:s}
nav.toc li a{display:flex;gap:8px;padding:6px 8px;border-radius:8px;color:var(--text);text-decoration:none;font-size:14px;line-height:1.35}
nav.toc li a::before{counter-increment:s;content:counter(s);color:var(--muted);min-width:18px;font-variant-numeric:tabular-nums}
nav.toc li a:hover{background:var(--bg)}
nav.toc li a.active{background:var(--accent-soft);color:var(--accent);font-weight:600}
main{min-width:0}
header.hero{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:28px 32px;margin-bottom:24px;box-shadow:var(--shadow)}
header.hero h1{margin:0 0 6px;font-size:30px;line-height:1.2}
header.hero .meta{color:var(--muted);font-size:14px;display:flex;flex-wrap:wrap;gap:6px 18px;align-items:center}
.toolbar{display:flex;gap:8px;margin-left:auto}
.toolbar button{border:1px solid var(--line);background:var(--bg);color:var(--text);border-radius:8px;padding:6px 10px;cursor:pointer;font-size:13px}
section.guide{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:28px 32px;margin-bottom:24px;box-shadow:var(--shadow)}
section.guide h2{margin:0 0 12px;font-size:24px;line-height:1.25}
section.guide>ol{counter-reset:step;list-style:none;padding:0;margin:20px 0}
section.guide>ol>li{counter-increment:step;position:relative;padding:0 0 18px 48px;margin-bottom:6px;border-left:2px solid var(--line);margin-left:15px}
section.guide>ol>li:last-child{border-left-color:transparent}
section.guide>ol>li::before{content:counter(step);position:absolute;left:-16px;top:-2px;width:30px;height:30px;border-radius:50%%;
background:var(--accent);color:#fff;font-weight:700;font-size:15px;display:grid;place-items:center;border:2px solid var(--panel);box-shadow:0 1px 4px rgba(0,0,0,.25)}
section.guide>ol>li>p:first-child{margin-top:0}
figure{margin:14px 0 6px;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:8px}
figure img{display:block;width:100%%;height:auto;border-radius:6px;cursor:zoom-in}
figcaption{font-size:13px;color:var(--muted);padding:6px 4px 0}
table{border-collapse:collapse;width:100%%;margin:16px 0;font-size:14.5px;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{background:var(--bg)}
code{background:var(--code);padding:1px 6px;border-radius:5px;font-size:.9em}
strong{font-weight:650}
.lightbox{position:fixed;inset:0;background:rgba(0,0,0,.85);display:none;align-items:flex-start;justify-content:center;overflow:auto;padding:24px;z-index:10;cursor:zoom-out}
.lightbox.open{display:flex}
.lightbox img{max-width:min(1440px,100%%);height:auto;border-radius:8px;box-shadow:0 10px 40px rgba(0,0,0,.5)}
.hidden{display:none!important}
footer{color:var(--muted);font-size:13px;text-align:center;padding:8px 0 32px}
@media (max-width:900px){.layout{grid-template-columns:1fr;gap:16px}nav.toc{position:static;max-height:none}
header.hero,section.guide{padding:20px 16px}section.guide>ol>li{padding-left:36px}}
@media print{nav.toc,.toolbar,.lightbox{display:none!important}.layout{display:block;padding:0}body{background:#fff}
header.hero,section.guide{box-shadow:none;border:0;padding:0 0 12px}figure{break-inside:avoid}section.guide{break-before:page}}
""" % {"accent": ACCENT}

JS = """
(function(){
const root=document.documentElement;
try{const t=localStorage.getItem('guide-theme');if(t)root.dataset.theme=t;}catch(e){}
document.getElementById('theme').onclick=()=>{const d=root.dataset.theme==='dark'||(!root.dataset.theme&&matchMedia('(prefers-color-scheme: dark)').matches);
root.dataset.theme=d?'light':'dark';try{localStorage.setItem('guide-theme',root.dataset.theme)}catch(e){}};
document.getElementById('print').onclick=()=>window.print();
const links=[...document.querySelectorAll('nav.toc li a')];
const secs=links.map(a=>document.querySelector(a.getAttribute('href')));
const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){links.forEach(l=>l.classList.toggle('active',l.getAttribute('href')==='#'+e.target.id));}})},{rootMargin:'0px 0px -70% 0px'});
secs.forEach(s=>s&&io.observe(s));
const q=document.getElementById('filter');
q.oninput=()=>{const v=q.value.trim().toLowerCase();secs.forEach((s,i)=>{const hit=!v||s.textContent.toLowerCase().includes(v);
s.classList.toggle('hidden',!hit);links[i].parentElement.classList.toggle('hidden',!hit);});};
const lb=document.getElementById('lightbox'),lbi=lb.querySelector('img');
document.querySelectorAll('figure img').forEach(i=>i.onclick=()=>{lbi.src=i.src;lbi.alt=i.alt;lb.classList.add('open')});
lb.onclick=()=>lb.classList.remove('open');
document.addEventListener('keydown',e=>{if(e.key==='Escape')lb.classList.remove('open')});
})();
"""


def slug(text: str) -> str:
	s = re.sub(r"<[^>]+>", "", text).lower()
	s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
	return s or "section"


def normalise_indent(md: str) -> str:
	"""Python-Markdown nests list content at 4 spaces; the guides indent with 3."""
	return re.sub(r"(?m)^ {3}(?=\S)", "    ", md)


def png_size(path: Path) -> tuple[int, int] | None:
	try:
		head = path.read_bytes()[:24]
	except OSError:
		return None
	if head[:8] != b"\x89PNG\r\n\x1a\n":
		return None
	return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")


def figures(body: str, base: Path) -> str:
	"""<p><img alt=X></p> -> <figure><img><figcaption>X</figcaption></figure>.

	Width/height are set from the file so lazy-loaded images reserve their space and
	links to sections land in the right place.
	"""
	def repl(m):
		img = m.group(1)
		alt = re.search(r'alt="([^"]*)"', img)
		src = re.search(r'src="([^"]+)"', img)
		cap = f"<figcaption>{alt.group(1)}</figcaption>" if alt else ""
		size = png_size(base / src.group(1)) if src else None
		attrs = 'loading="lazy" ' + (f'width="{size[0]}" height="{size[1]}" ' if size else "")
		img = img.replace("<img ", "<img " + attrs, 1)
		return f"<figure>{img}{cap}</figure>"
	return re.sub(r"<p>\s*(<img [^>]+>)\s*</p>", repl, body)


def embed_images(body: str, base: Path) -> str:
	def repl(m):
		src = m.group(1)
		path = base / src
		if src.startswith(("data:", "http")) or not path.is_file():
			return m.group(0)
		mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
		data = base64.b64encode(path.read_bytes()).decode()
		return f'src="data:{mime};base64,{data}"'
	return re.sub(r'src="([^"]+)"', repl, body)


def build_guide(folder: Path, embed: bool) -> dict | None:
	meta_file = folder / "guide.json"
	md_files = sorted(folder.glob("*-admin-guide.md"))
	if not meta_file.is_file() or not md_files:
		return None
	meta = json.loads(meta_file.read_text())
	md = md_files[0].read_text()

	# Title and the "Updated … · Online version" line come from guide.json, not the Markdown.
	md = re.sub(r"\A# .*\n+", "", md)
	updated = re.search(r"(?m)^Updated (\d{4}-\d{2}-\d{2})", md)
	md = re.sub(r"(?m)^Updated .*\n+", "", md, count=1)
	title = meta.get("title") or folder.name

	body = markdown.markdown(normalise_indent(md), extensions=["tables", "sane_lists"])
	body = figures(body, folder)
	if embed:
		body = embed_images(body, folder)

	# Split into one <section> per h2, collecting the table of contents.
	parts = re.split(r"(<h2>.*?</h2>)", body)
	intro, sections, toc = parts[0], [], []
	for i in range(1, len(parts), 2):
		heading = parts[i]
		text = re.sub(r"</?h2>", "", heading)
		sid = slug(text)
		toc.append((sid, text))
		sections.append(f'<section class="guide" id="{sid}">{heading}{parts[i + 1]}</section>')

	doc = meta.get("doc") or {}
	online = doc.get("url")
	answers = meta.get("answers") or {}
	shots = len(re.findall(r"<figure>", body))
	day = updated.group(1) if updated else date.today().isoformat()
	meta_bits = [f"Updated {day}", f"{len(toc)} sections", f"{shots} screenshots"]
	if answers.get("audience"):
		meta_bits.append(f"For {html.escape(answers['audience'])}")
	if online:
		meta_bits.append(f'<a href="{html.escape(online)}">Online version</a>')

	toc_html = "".join(f'<li><a href="#{sid}">{t}</a></li>' for sid, t in toc)
	page = f"""<!doctype html>
<html lang="{html.escape(answers.get('language') or 'en')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="layout">
<nav class="toc" aria-label="Contents">
<a class="back" href="../index.html">&larr; All guides</a>
<h2>Contents</h2>
<input id="filter" type="search" placeholder="Search this guide" aria-label="Search this guide">
<ol>{toc_html}</ol>
</nav>
<main>
<header class="hero">
<h1>{html.escape(title)}</h1>
<div class="meta">{"<span>" + "</span><span>".join(meta_bits) + "</span>"}
<div class="toolbar"><button id="theme" type="button">Light / dark</button><button id="print" type="button">Print / PDF</button></div></div>
{intro}
</header>
{"".join(sections)}
<footer>Generated from {html.escape(md_files[0].name)} by the admin-guide-screenshots skill.</footer>
</main>
</div>
<div class="lightbox" id="lightbox" role="dialog" aria-label="Screenshot"><img alt=""></div>
<script>{JS}</script>
</body>
</html>
"""
	out = folder / "index.html"
	out.write_text(page)
	first_img = re.search(r'<img [^>]*src="(img/[^"]+)"', body)
	return {"folder": folder.name, "title": title, "sections": len(toc), "shots": shots, "updated": day,
		"online": online, "thumb": first_img.group(1) if first_img else None,
		"audience": answers.get("audience"), "size": out.stat().st_size}


def build_index(root: Path, guides: list[dict]) -> Path:
	cards = []
	for g in sorted(guides, key=lambda g: g["title"].lower()):
		thumb = f'<img src="{g["folder"]}/{g["thumb"]}" alt="" loading="lazy">' if g["thumb"] else ""
		online = f' · <a href="{html.escape(g["online"])}">online</a>' if g.get("online") else ""
		aud = f'<p class="aud">For {html.escape(g["audience"])}</p>' if g.get("audience") else ""
		cards.append(f'<article class="card"><a class="cover" href="{g["folder"]}/index.html">{thumb}</a>'
			f'<div class="body"><h2><a href="{g["folder"]}/index.html">{html.escape(g["title"])}</a></h2>{aud}'
			f'<p class="meta">{g["sections"]} sections · {g["shots"]} screenshots · updated {g["updated"]}{online}</p></div></article>')
	page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Admin Guides</title>
<style>{CSS}
.wrap{{max-width:1100px;margin:0 auto;padding:32px 16px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden;box-shadow:var(--shadow)}}
.card .cover{{display:block;aspect-ratio:16/9;background:var(--bg);overflow:hidden}}
.card .cover img{{width:100%;height:100%;object-fit:cover;object-position:top left}}
.card .body{{padding:14px 18px 16px}}
.card h2{{margin:0 0 4px;font-size:19px}}.card h2 a{{color:var(--text);text-decoration:none}}
.card .meta,.card .aud{{margin:2px 0;color:var(--muted);font-size:13.5px}}
</style>
</head>
<body>
<div class="wrap">
<header class="hero"><h1>Admin Guides</h1><div class="meta"><span>{len(guides)} guides</span><span>Step-by-step guides with annotated screenshots</span></div></header>
<div class="grid">{"".join(cards)}</div>
</div>
</body>
</html>
"""
	out = root / "index.html"
	out.write_text(page)
	return out


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("root", nargs="?", default="docs/admin-guides")
	parser.add_argument("--guide", nargs="*", help="only these guide folders")
	parser.add_argument("--embed", action="store_true", help="inline screenshots (single-file pages)")
	parser.add_argument("--zip", nargs="?", const="", default=None, metavar="FILE",
		help="also zip the pages and their screenshots (default: <root>-html-<date>.zip next to the guides folder)")
	args = parser.parse_args()
	root = Path(args.root)

	built = []
	for folder in sorted(p for p in root.iterdir() if p.is_dir()):
		info = build_guide(folder, args.embed) if (not args.guide or folder.name in args.guide) else None
		if info:
			built.append(info)
			print(f"OK   {folder / 'index.html'}  ({info['sections']} sections, {info['shots']} screenshots, {info['size'] // 1024} KB)")
	# The index lists every guide that has a page, built now or before.
	listed = []
	for folder in sorted(p for p in root.iterdir() if p.is_dir()):
		hit = next((b for b in built if b["folder"] == folder.name), None)
		if hit:
			listed.append(hit)
		elif (folder / "index.html").is_file() and (folder / "guide.json").is_file():
			meta = json.loads((folder / "guide.json").read_text())
			listed.append({"folder": folder.name, "title": meta.get("title", folder.name), "sections": len(meta.get("sections", [])),
				"shots": len(list((folder / "img").glob("*.png"))), "updated": "", "online": (meta.get("doc") or {}).get("url"),
				"thumb": None, "audience": (meta.get("answers") or {}).get("audience")})
	print(f"OK   {build_index(root, listed)}  ({len(listed)} guides)")

	if args.zip is not None:
		folders = [g["folder"] for g in listed if not args.guide or g["folder"] in args.guide]
		target = Path(args.zip) if args.zip else root.parent / f"{root.name}-html-{date.today().isoformat()}.zip"
		count, size = build_zip(root, folders, target)
		print(f"OK   {target}  ({count} files, {size // 1024} KB)")


def build_zip(root: Path, folders: list[str], target: Path) -> tuple[int, int]:
	"""Zip the index page, each guide page and only the screenshots those pages use.

	Working files (guide.json, shots.json, inventory.md, the Markdown copy) stay out: the zip is
	for readers. Paths inside start with the guides folder name, so it unzips into one folder.
	"""
	import zipfile

	target.parent.mkdir(parents=True, exist_ok=True)
	files = [root / "index.html"]
	for name in folders:
		page = root / name / "index.html"
		if not page.is_file():
			continue
		files.append(page)
		for src in sorted(set(re.findall(r'src="(img/[^"]+)"', page.read_text()))):
			if (root / name / src).is_file():
				files.append(root / name / src)
	with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
		for f in files:
			z.write(f, Path(root.name) / f.relative_to(root))
	return len(files), target.stat().st_size


if __name__ == "__main__":
	main()
