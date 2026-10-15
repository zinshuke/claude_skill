#!/usr/bin/env python3
"""Capture admin-guide screenshots with numbered highlight boxes.

Usage:
    python3 shoot.py SHOTS.json [--out DIR] [--env-file FILE] [--only NAME ...]

SHOTS.json (see ../shots.example.json):
    base_url    site root, e.g. http://localhost:3000
    login       optional; defaults to the Joomla administrator login form
    viewport    {"width": 1440, "height": 900}
    color       box/badge color, any CSS color (default #e5262f); also per shot and per highlight
    crop        true (default): crop each image to its boxes plus padding; false: whole page;
                or {"padding": 60, "min_width": 800, "min_height": 400}; also per shot
    hide        selectors hidden on every shot (debug bars, cookie banners)
    blur        selectors blurred on every shot (fields holding secrets or IDs)
    redact      regexes; matching text anywhere on the page (text, field values, selected
                options) is masked (x/0) and blurred. Email addresses are always blurred unless
                "redact_emails": false. Also per shot.
    shots       list of {name, url, actions?, highlights, hide?, blur?, full_page?, color?,
                crop?, crop_include?, redact?}; a highlight is {selector, label?, note?, color?,
                badge?, padding?}

Credentials come from ADMIN_GUIDE_USER / ADMIN_GUIDE_PASS, read from the
environment or from --env-file (KEY=VALUE lines). Never put them in SHOTS.json.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

JOOMLA_LOGIN = {
	"url": "/administrator/index.php",
	"user": "#mod-login-username",
	"pass": "#mod-login-password",
	"submit": "#btn-login-submit",
	"done": "#header",
}

BOX_COLOR = "#e5262f"
CROP = {"padding": 60, "min_width": 800, "min_height": 400}

# Draws one box + tag (numbered badge, optional note) per highlight, in document
# coordinates so a full-page screenshot keeps them in place.
HIGHLIGHT_JS = """
([items, defaultColor]) => {
	const missing = [];
	// Badge text in black or white, whichever reads better on the box color.
	const textOn = (color) => {
		const probe = document.createElement('div');
		probe.style.color = color;
		document.body.appendChild(probe);
		const [r, g, b] = (getComputedStyle(probe).color.match(/[\\d.]+/g) || [0, 0, 0]).map(Number);
		probe.remove();
		return 0.299 * r + 0.587 * g + 0.114 * b > 160 ? '#111' : '#fff';
	};
	const docWidth = document.documentElement.scrollWidth;
	const font = 'system-ui, -apple-system, Segoe UI, sans-serif';
	for (const it of items) {
		const el = document.querySelector(it.selector);
		if (!el) { missing.push(it.selector); continue; }
		el.scrollIntoView({block: 'center'});
		const r = el.getBoundingClientRect();
		const pad = it.padding ?? 6;
		const color = it.color || defaultColor;
		const boxLeft = r.left + scrollX - pad, boxTop = r.top + scrollY - pad;
		const boxWidth = r.width + pad * 2, boxHeight = r.height + pad * 2;
		const box = document.createElement('div');
		box.className = 'ags-box';
		Object.assign(box.style, {
			position: 'absolute', zIndex: 2147483646, pointerEvents: 'none',
			left: boxLeft + 'px', top: boxTop + 'px', width: boxWidth + 'px', height: boxHeight + 'px',
			border: '3px solid ' + color, borderRadius: '6px',
			boxShadow: '0 0 0 3px rgba(255,255,255,.85), 0 2px 10px rgba(0,0,0,.25)',
			boxSizing: 'border-box',
		});
		document.body.appendChild(box);
		const label = it.label === undefined || it.label === null ? '' : String(it.label);
		const note = it.note ? String(it.note) : '';
		if (!label && !note) continue;
		// Badge and note form one tag, placed outside the box so it never covers the target.
		const tag = document.createElement('div');
		tag.className = 'ags-tag';
		Object.assign(tag.style, {
			position: 'absolute', zIndex: 2147483647, pointerEvents: 'none', visibility: 'hidden',
			display: 'flex', alignItems: 'stretch', maxWidth: '340px', overflow: 'hidden',
			borderRadius: '16px', border: '2px solid ' + (note ? color : '#fff'), background: '#fff',
			boxShadow: '0 2px 6px rgba(0,0,0,.35)', boxSizing: 'border-box',
		});
		if (label) {
			const b = document.createElement('div');
			b.textContent = label;
			Object.assign(b.style, {
				display: 'flex', alignItems: 'center', justifyContent: 'center', flex: '0 0 auto',
				minWidth: '26px', minHeight: '26px', padding: '0 7px', boxSizing: 'border-box',
				background: color, color: textOn(color), font: '700 16px/1 ' + font,
			});
			tag.appendChild(b);
		}
		if (note) {
			const n = document.createElement('div');
			n.textContent = note;
			Object.assign(n.style, {
				padding: '4px 10px', color: '#1d1d1f', background: '#fff',
				font: '600 14px/1.3 ' + font, whiteSpace: 'normal', alignSelf: 'center',
			});
			tag.appendChild(n);
		}
		document.body.appendChild(tag);
		const w = tag.offsetWidth, h = tag.offsetHeight;
		const spots = {
			left: [boxLeft - w - 6, boxTop],
			right: [boxLeft + boxWidth + 6, boxTop],
			top: [Math.min(boxLeft, docWidth - w - 2), boxTop - h - 6],
			bottom: [Math.min(boxLeft, docWidth - w - 2), boxTop + boxHeight + 6],
		};
		const fits = ([x, y]) => x >= 2 && y >= 2 && x + w <= docWidth - 2;
		const order = [it.badge || 'left', 'left', 'top', 'right', 'bottom'];
		const [x, y] = spots[order.find((k) => spots[k] && fits(spots[k])) || 'bottom'];
		Object.assign(tag.style, {left: Math.max(2, x) + 'px', top: Math.max(2, y) + 'px', visibility: 'visible'});
	}
	window.scrollTo(0, 0);
	return missing;
}
"""

# Area around the boxes, tags and extra selectors, plus padding, grown to a minimum
# size and kept inside the page (or the viewport when the shot is not full page).
CROP_JS = """
([extra, crop, fullPage]) => {
	const els = [...document.querySelectorAll('.ags-box, .ags-tag')];
	for (const s of extra) els.push(...document.querySelectorAll(s));
	const offX = fullPage ? scrollX : 0, offY = fullPage ? scrollY : 0;
	let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
	for (const el of els) {
		const r = el.getBoundingClientRect();
		if (!r.width && !r.height) continue;
		x1 = Math.min(x1, r.left + offX); y1 = Math.min(y1, r.top + offY);
		x2 = Math.max(x2, r.right + offX); y2 = Math.max(y2, r.bottom + offY);
	}
	if (x1 === Infinity) return null;
	const maxW = fullPage ? document.documentElement.scrollWidth : innerWidth;
	const maxH = fullPage ? document.documentElement.scrollHeight : innerHeight;
	const fit = (a, b, min, max) => {
		a -= crop.padding; b += crop.padding;
		if (b - a < min) { const c = (a + b) / 2; a = c - min / 2; b = c + min / 2; }
		if (a < 0) { b -= a; a = 0; }
		if (b > max) { a -= b - max; b = max; }
		return [Math.max(0, Math.round(a)), Math.round(Math.min(b, max))];
	};
	const [left, right] = fit(x1, x2, crop.min_width, maxW);
	const [top, bottom] = fit(y1, y2, crop.min_height, maxH);
	return {x: left, y: top, width: right - left, height: bottom - top};
}
"""


EMAIL_RE = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"

# Hides every match of the patterns: the characters are replaced first (letters -> x,
# digits -> 0) so the image never holds the real value, then blurred. A form field or select
# showing a match is masked and blurred whole. Returns how many places were hidden.
REDACT_JS = """
(patterns) => {
	const res = patterns.map((p) => new RegExp(p, 'gi'));
	const hit = (s) => res.some((r) => { r.lastIndex = 0; return r.test(s); });
	const blur = 'blur(5px)';
	const mask = (s) => s.replace(/[A-Za-z]/g, 'x').replace(/[0-9]/g, '0');
	let count = 0;
	const docs = [document];
	for (const f of document.querySelectorAll('iframe')) {
		try { if (f.contentDocument && f.contentDocument.body) docs.push(f.contentDocument); } catch (e) {}
	}
	for (const doc of docs) {
		for (const el of doc.querySelectorAll('input, textarea, select')) {
			if (el.dataset.agsRedact) continue;
			const opt = el.tagName === 'SELECT' ? el.selectedOptions[0] : null;
			const v = opt ? opt.text : (el.tagName === 'SELECT' || el.type === 'password' ? '' : el.value);
			if (!v || !hit(v)) continue;
			if (opt) opt.text = mask(v); else el.value = mask(v);
			el.style.filter = blur;
			el.dataset.agsRedact = '1';
			count++;
		}
		const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, {acceptNode: (n) => {
			const p = n.parentElement;
			return p && !p.dataset.agsRedact && !/^(SCRIPT|STYLE|NOSCRIPT|OPTION|TEXTAREA)$/.test(p.tagName) && hit(n.nodeValue)
				? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
		}});
		const nodes = [];
		while (walker.nextNode()) nodes.push(walker.currentNode);
		for (const node of nodes) {
			const text = node.nodeValue;
			const ranges = [];
			for (const r of res) {
				r.lastIndex = 0;
				let m;
				while ((m = r.exec(text))) {
					if (!m[0]) { r.lastIndex++; continue; }
					ranges.push([m.index, m.index + m[0].length]);
				}
			}
			ranges.sort((a, b) => a[0] - b[0]);
			const merged = [];
			for (const r of ranges) {
				const last = merged[merged.length - 1];
				if (last && r[0] <= last[1]) last[1] = Math.max(last[1], r[1]); else merged.push(r);
			}
			const frag = doc.createDocumentFragment();
			let pos = 0;
			for (const [a, b] of merged) {
				frag.append(text.slice(pos, a));
				const span = doc.createElement('span');
				span.textContent = mask(text.slice(a, b));
				span.dataset.agsRedact = '1';
				Object.assign(span.style, {filter: blur, display: 'inline-block'});
				frag.append(span);
				pos = b;
				count++;
			}
			frag.append(text.slice(pos));
			node.replaceWith(frag);
		}
	}
	return count;
}
"""


def redact_patterns(spec: dict, shot: dict) -> list[str]:
	emails = [EMAIL_RE] if spec.get("redact_emails", True) and shot.get("redact_emails", True) else []
	return emails + spec.get("redact", []) + shot.get("redact", [])


def crop_settings(spec: dict, shot: dict) -> dict | None:
	"""Merged crop options for a shot, or None for an uncropped page/viewport."""
	merged = dict(CROP)
	for value in (spec.get("crop", True), shot.get("crop", True)):
		if value is False:
			return None
		if isinstance(value, dict):
			merged.update(value)
	return merged


def load_env_file(path: Path) -> None:
	if not path.is_file():
		return
	for line in path.read_text().splitlines():
		line = line.strip()
		if not line or line.startswith("#") or "=" not in line:
			continue
		key, value = line.split("=", 1)
		os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def style_selectors(page: Page, hide: list[str], blur: list[str]) -> None:
	css = ""
	if hide:
		css += ",".join(hide) + "{display:none!important}"
	if blur:
		css += ",".join(blur) + "{filter:blur(6px)!important}"
	if css:
		# Also same-origin iframes (modal dialogs such as media pickers), which keep their own debug bars.
		for frame in page.frames:
			try:
				frame.add_style_tag(content=css)
			except Exception:
				pass


def run_action(page: Page, action: dict) -> None:
	if "click" in action:
		page.click(action["click"])
	elif "fill" in action:
		selector, value = action["fill"]
		page.fill(selector, value)
	elif "select" in action:
		selector, value = action["select"]
		page.select_option(selector, value)
	elif "hover" in action:
		page.hover(action["hover"])
	elif "wait" in action:
		page.wait_for_selector(action["wait"], state="visible")
	elif "wait_ms" in action:
		page.wait_for_timeout(int(action["wait_ms"]))
	elif "eval" in action:
		page.evaluate(action["eval"])
	else:
		raise ValueError(f"Unknown action: {action}")


def login(page: Page, base_url: str, cfg: dict) -> None:
	user = os.environ.get("ADMIN_GUIDE_USER")
	password = os.environ.get("ADMIN_GUIDE_PASS")
	if not user or not password:
		sys.exit("ADMIN_GUIDE_USER / ADMIN_GUIDE_PASS are not set (env or --env-file).")
	page.goto(base_url + cfg["url"])
	if page.query_selector(cfg["user"]) is None:
		return  # already logged in
	page.fill(cfg["user"], user)
	page.fill(cfg["pass"], password)
	page.click(cfg["submit"])
	page.wait_for_selector(cfg["done"], timeout=20000)


def main() -> int:
	parser = argparse.ArgumentParser()
	parser.add_argument("shots")
	parser.add_argument("--out", default=None, help="output dir (default: next to SHOTS.json)")
	parser.add_argument("--env-file", default=".claude/admin-guide.env")
	parser.add_argument("--only", nargs="*", help="shot names to (re)take")
	args = parser.parse_args()

	load_env_file(Path(args.env_file))
	spec_path = Path(args.shots)
	spec = json.loads(spec_path.read_text())
	out = Path(args.out) if args.out else spec_path.parent
	out.mkdir(parents=True, exist_ok=True)

	base_url = spec["base_url"].rstrip("/")
	login_cfg = {**JOOMLA_LOGIN, **spec.get("login", {})}
	viewport = spec.get("viewport", {"width": 1440, "height": 900})
	failures = 0

	with sync_playwright() as p:
		try:
			browser = p.chromium.launch()
		except Exception:
			# Bundled browser not downloaded for this Playwright version: use installed Chrome.
			browser = p.chromium.launch(channel="chrome", headless=True)
		context = browser.new_context(viewport=viewport, device_scale_factor=spec.get("scale", 1))
		page = context.new_page()
		login(page, base_url, login_cfg)

		for shot in spec["shots"]:
			if args.only and shot["name"] not in args.only:
				continue
			page.goto(base_url + shot["url"])
			page.wait_for_load_state("networkidle")
			try:
				for action in shot.get("actions", []):
					run_action(page, action)
			except Exception as e:
				failures += 1
				print(f"FAIL {shot['name']}: action failed, shot skipped: {str(e).splitlines()[0]}")
				continue
			style_selectors(
				page,
				spec.get("hide", []) + shot.get("hide", []),
				spec.get("blur", []) + shot.get("blur", []),
			)
			patterns = redact_patterns(spec, shot)
			redacted = page.evaluate(REDACT_JS, patterns) if patterns else 0
			# Let charts finish resizing/animating after the injected styles changed the layout.
			page.wait_for_timeout(int(shot.get("settle_ms", 300)))
			color = shot.get("color", spec.get("color", BOX_COLOR))
			missing = page.evaluate(HIGHLIGHT_JS, [shot.get("highlights", []), color])
			page.wait_for_timeout(int(shot.get("settle_ms", 300)))
			# Things that must be open in the picture but close when boxes are drawn (dropdown menus).
			try:
				for action in shot.get("post_actions", []):
					run_action(page, action)
			except Exception as e:
				print(f"WARN {shot['name']}: post action failed: {str(e).splitlines()[0]}")
			if patterns:
				# Menus opened by post actions show new text.
				redacted += page.evaluate(REDACT_JS, patterns)
			file = out / f"{shot['name']}.png"
			full_page = shot.get("full_page", True)
			crop = crop_settings(spec, shot)
			clip = page.evaluate(CROP_JS, [shot.get("crop_include", []), crop, full_page]) if crop else None
			page.screenshot(path=str(file), full_page=full_page, clip=clip)
			if missing:
				failures += 1
				print(f"WARN {file}: highlight selector not found: {', '.join(missing)}")
			else:
				print(f"OK   {file}" + (f"  (blurred {redacted} personal item(s))" if redacted else ""))

		browser.close()

	return 1 if failures else 0


if __name__ == "__main__":
	sys.exit(main())
