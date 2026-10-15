#!/usr/bin/env python3
"""List a Joomla site's extensions from their manifests, to choose a guide's scope.

Usage: python3 list_extensions.py [SITE_ROOT] [--all]

Third-party only by default (author is not "Joomla! Project"); --all includes core.
"""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

PATTERNS = [
	("component", "administrator/components/*/*.xml"),
	("module (site)", "modules/*/*.xml"),
	("module (admin)", "administrator/modules/*/*.xml"),
	("plugin", "plugins/*/*/*.xml"),
	("template (site)", "templates/*/templateDetails.xml"),
	("template (admin)", "administrator/templates/*/templateDetails.xml"),
	("package", "administrator/manifests/packages/*.xml"),
]


def read_manifest(path: Path) -> dict | None:
	try:
		root = ET.parse(path).getroot()
	except ET.ParseError:
		return None
	if root.tag != "extension":
		return None
	text = lambda tag: (root.findtext(tag) or "").strip()
	return {"name": text("name"), "author": text("author"), "version": text("version")}


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("root", nargs="?", default=".")
	parser.add_argument("--all", action="store_true")
	args = parser.parse_args()
	root = Path(args.root)

	rows = []
	for kind, pattern in PATTERNS:
		for path in sorted(root.glob(pattern)):
			info = read_manifest(path)
			if not info:
				continue
			core = info["author"].lower().startswith("joomla! project")
			if core and not args.all:
				continue
			group = path.parent.parent.name if kind == "plugin" else "-"
			rows.append((kind, group, info["name"], info["version"], info["author"], str(path.parent.relative_to(root))))

	print("type\tgroup\tname\tversion\tauthor\tpath")
	for row in rows:
		print("\t".join(row))


if __name__ == "__main__":
	main()
