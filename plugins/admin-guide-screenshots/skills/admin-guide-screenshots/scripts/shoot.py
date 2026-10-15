#!/usr/bin/env python3
"""Capture admin-guide screenshots with numbered highlight boxes.

Usage:
    python3 shoot.py SHOTS.json [--out DIR] [--env-file FILE] [--only NAME ...]

SHOTS.json (see ../shots.example.json):
    base_url    site root, e.g. http://localhost:3000
    login       optional; defaults to the Joomla administrator login form
    viewport    {"width": 1440, "height": 900}
    hide        selectors hidden on every shot (debug bars, cookie banners)
    blur        selectors blurred on every shot (emails, secrets)
    shots       list of {name, url, actions?, highlights, hide?, blur?, full_page?}

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

# Draws one box + numbered badge per highlight, in document coordinates so a
# full-page screenshot keeps them in place.
HIGHLIGHT_JS = """
([items, color]) => {
	const missing = [];
	for (const it of items) {
		const el = document.querySelector(it.selector);
		if (!el) { missing.push(it.selector); continue; }
		el.scrollIntoView({block: 'center'});
		const r = el.getBoundingClientRect();
		const pad = it.padding ?? 6;
		const box = document.createElement('div');
		box.className = 'ags-box';
		Object.assign(box.style, {
			position: 'absolute', zIndex: 2147483646, pointerEvents: 'none',
			left: (r.left + scrollX - pad) + 'px', top: (r.top + scrollY - pad) + 'px',
			width: (r.width + pad * 2) + 'px', height: (r.height + pad * 2) + 'px',
			border: '3px solid ' + color, borderRadius: '6px',
			boxShadow: '0 0 0 3px rgba(255,255,255,.85), 0 2px 10px rgba(0,0,0,.25)',
			boxSizing: 'border-box',
		});
		document.body.appendChild(box);
		if (it.label !== undefined && it.label !== null && it.label !== '') {
			const b = document.createElement('div');
			b.className = 'ags-badge';
			b.textContent = String(it.label);
			const size = 30;
			const boxLeft = r.left + scrollX - pad;
			const boxTop = r.top + scrollY - pad;
			// Outside the box's left edge so it never covers the target; on the corner when there is no room.
			const width = Math.max(size, 12 + 10 * String(it.label).length);
			const boxRight = boxLeft + r.width + pad * 2;
			let left, top;
			if (it.badge === 'top') {
				left = boxLeft + (r.width + pad * 2 - width) / 2;
				top = Math.max(2, boxTop - size - 4);
			} else {
				const outside = it.badge === 'right' ? boxRight + 6 : boxLeft - width - 6;
				const fits = it.badge === 'right' ? outside + width <= document.documentElement.scrollWidth - 2 : outside >= 2;
				left = fits ? outside : Math.max(2, boxLeft - size / 2);
				top = fits ? boxTop : Math.max(2, boxTop - size / 2);
			}
			Object.assign(b.style, {
				position: 'absolute', zIndex: 2147483647, pointerEvents: 'none',
				left: left + 'px', top: top + 'px', width: width + 'px', height: size + 'px',
				lineHeight: size + 'px', borderRadius: size / 2 + 'px', background: color, color: '#fff',
				font: '700 16px/30px system-ui, -apple-system, Segoe UI, sans-serif',
				textAlign: 'center', border: '2px solid #fff',
				boxShadow: '0 2px 6px rgba(0,0,0,.35)',
			});
			document.body.appendChild(b);
		}
	}
	window.scrollTo(0, 0);
	return missing;
}
"""


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
			# Let charts finish resizing/animating after the injected styles changed the layout.
			page.wait_for_timeout(int(shot.get("settle_ms", 300)))
			missing = page.evaluate(HIGHLIGHT_JS, [shot.get("highlights", []), spec.get("color", BOX_COLOR)])
			page.wait_for_timeout(int(shot.get("settle_ms", 300)))
			# Things that must be open in the picture but close when boxes are drawn (dropdown menus).
			try:
				for action in shot.get("post_actions", []):
					run_action(page, action)
			except Exception as e:
				print(f"WARN {shot['name']}: post action failed: {str(e).splitlines()[0]}")
			file = out / f"{shot['name']}.png"
			page.screenshot(path=str(file), full_page=shot.get("full_page", True))
			if missing:
				failures += 1
				print(f"WARN {file}: highlight selector not found: {', '.join(missing)}")
			else:
				print(f"OK   {file}")

		browser.close()

	return 1 if failures else 0


if __name__ == "__main__":
	sys.exit(main())
