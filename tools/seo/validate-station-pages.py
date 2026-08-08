#!/usr/bin/env python3
"""Validate the RipCat SEO station-page pilot.

Checks the one-time Tier-2 pilot contract from marketing/playbooks/seo-station-pages.md:
- California index + 25 station pages exist.
- Each station page has JSON-LD Place and BreadcrumbList.
- Smart App Banner meta is present.
- App Store link uses ct=seo-station-{id}.
- Nearby links, state-index link, NOAA station facts, and not-navigation framing exist.
- Pages avoid static live/current/today tide-height claims.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "tides" / "ca"
EXPECTED_COUNT = 25

LIVE_TIDE_CLAIM_PATTERNS = [
    re.compile(r"\b(today'?s|current|right now|now)\s+(tide|water)\s+(is|height|at)\b", re.I),
    re.compile(r"\b(high|low)\s+tide\s+(is|at|will be)\s+\d", re.I),
]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.h1: list[str] = []
        self._in_h1 = False
        self.links: list[str] = []
        self.meta: list[dict[str, str]] = []
        self.scripts: list[tuple[str, str]] = []
        self._script_type = ""
        self._script_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k: v or "" for k, v in attrs}
        if tag == "h1":
            self._in_h1 = True
        elif tag == "a":
            self.links.append(attr.get("href", ""))
        elif tag == "meta":
            self.meta.append(attr)
        elif tag == "script":
            self._script_type = attr.get("type", "")
            self._script_chunks = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1":
            self._in_h1 = False
        elif tag == "script":
            if self._script_type:
                self.scripts.append((self._script_type, "".join(self._script_chunks)))
            self._script_type = ""
            self._script_chunks = []

    def handle_data(self, data: str) -> None:
        if self._in_h1:
            self.h1.append(data)
        if self._script_type:
            self._script_chunks.append(data)


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def script_types(parser: PageParser) -> set[str]:
    found = set()
    for typ, body in parser.scripts:
        if typ != "application/ld+json":
            continue
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            continue
        found.add(str(data.get("@type", "")))
    return found


def validate_station_page(path: Path) -> list[str]:
    errors: list[str] = []
    html = path.read_text(encoding="utf-8")
    parser = parse_page(path)
    slug = path.parent.name
    station_id_match = re.search(r"-(\d{7})$", slug)
    require(bool(station_id_match), errors, f"{path}: slug missing station id")
    station_id = station_id_match.group(1) if station_id_match else "UNKNOWN"

    h1 = " ".join(x.strip() for x in parser.h1).strip()
    require(h1.endswith("Tide Chart & Times"), errors, f"{path}: H1 not station tide title: {h1!r}")
    require(f"NOAA station {station_id}" in html, errors, f"{path}: missing station id text")
    require("Coordinates" in html, errors, f"{path}: missing coordinates fact")
    require("Region" in html, errors, f"{path}: missing region fact")
    require("Station type" in html, errors, f"{path}: missing station type fact")
    require("Predictions" in html and "navigation advice" in html, errors, f"{path}: missing predictions/not-navigation framing")

    meta_names = {(m.get("name") or m.get("property"), m.get("content", "")) for m in parser.meta}
    require(any(name == "apple-itunes-app" and "app-id=6760085664" in content for name, content in meta_names), errors, f"{path}: missing smart app banner")

    ld_types = script_types(parser)
    require("Place" in ld_types, errors, f"{path}: missing JSON-LD Place")
    require("BreadcrumbList" in ld_types, errors, f"{path}: missing JSON-LD BreadcrumbList")

    station_links = [href for href in parser.links if href.startswith("/tides/ca/") and href != "/tides/ca/" and href != f"/tides/ca/{slug}/"]
    require(len(station_links) >= 5, errors, f"{path}: expected at least 5 nearby station links, found {len(station_links)}")
    require("/tides/ca/" in parser.links, errors, f"{path}: missing state index link")

    app_links = [href for href in parser.links if "apps.apple.com" in href]
    require(any(parse_qs(urlparse(href).query).get("ct") == [f"seo-station-{station_id}"] for href in app_links), errors, f"{path}: missing App Store ct=seo-station-{station_id}")

    claim_scan = re.sub(r"Static pages do not claim today'?s tide height;", "", html, flags=re.I)
    for pattern in LIVE_TIDE_CLAIM_PATTERNS:
        require(not pattern.search(claim_scan), errors, f"{path}: possible static live tide claim: {pattern.pattern}")
    return errors


def main() -> int:
    errors: list[str] = []
    require((STATE_DIR / "index.html").exists(), errors, "missing /tides/ca/index.html")
    station_pages = sorted(p for p in STATE_DIR.glob("*/index.html") if p.parent.name != "index")
    require(len(station_pages) == EXPECTED_COUNT, errors, f"expected {EXPECTED_COUNT} station pages, found {len(station_pages)}")
    for page in station_pages:
        errors.extend(validate_station_page(page))

    sitemap = ROOT / "sitemap.xml"
    sitemap_text = sitemap.read_text(encoding="utf-8") if sitemap.exists() else ""
    require("https://ripcat.dev/tides/ca/" in sitemap_text, errors, "sitemap missing CA index")
    for page in station_pages:
        require(f"https://ripcat.dev/tides/ca/{page.parent.name}/" in sitemap_text, errors, f"sitemap missing {page.parent.name}")

    if errors:
        print("Station-page validation FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Station-page validation passed: {len(station_pages)}/{EXPECTED_COUNT} pages + CA index")
    return 0


if __name__ == "__main__":
    sys.exit(main())
