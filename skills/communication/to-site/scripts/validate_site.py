#!/usr/bin/env python3
"""Validate a built static site against its public semantic map."""

import argparse
import json
import pathlib
import re
import sys


PRIVATE_MARKERS = ("file://", "/Users/", "/home/", "/workspace/", ".hermes/", "BEGIN PRIVATE KEY", "api_key=")
ATTRIBUTE = re.compile(r'data-(claim|source)-id=["\']([^"\']+)["\']')
HREF = re.compile(r'href=["\']([^"\']+)["\']')


def html_files(dist):
    return sorted(pathlib.Path(dist).rglob("*.html"))


def validate_dist(dist, semantic_map_path):
    dist = pathlib.Path(dist)
    semantic_map = json.loads(pathlib.Path(semantic_map_path).read_text(encoding="utf-8"))
    failures = []
    required_pages = (dist / "index.html", dist / "mechanism" / "index.html", dist / "evidence" / "index.html")
    for page in required_pages:
        if not page.exists():
            failures.append("required page is missing: %s" % page.relative_to(dist))
    rendered_claims = set()
    rendered_sources = set()
    pages = html_files(dist)
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        for marker in PRIVATE_MARKERS:
            if marker in text:
                failures.append("private path leak in %s: %s" % (page.relative_to(dist), marker))
        for kind, identifier in ATTRIBUTE.findall(text):
            (rendered_claims if kind == "claim" else rendered_sources).add(identifier)
        for href in HREF.findall(text):
            if href.startswith(("http://", "https://", "mailto:", "data:", "#")):
                continue
            target = href.split("#", 1)[0]
            if not target:
                continue
            resolved = (dist / target.lstrip("/") / "index.html") if target.endswith("/") else (dist / target.lstrip("/"))
            if not resolved.exists():
                failures.append("broken internal link in %s: %s" % (page.relative_to(dist), href))
    for claim_id in semantic_map.get("claims", {}):
        if claim_id not in rendered_claims:
            failures.append("claim %s is not rendered in dist" % claim_id)
    for source_id in semantic_map.get("sources", []):
        if source_id not in rendered_sources:
            failures.append("source %s is not rendered in dist" % source_id)
    return {
        "passed": not failures,
        "failures": failures,
        "rendered_claim_ids": sorted(rendered_claims),
        "rendered_source_ids": sorted(rendered_sources),
        "pages_checked": [str(page.relative_to(dist)) for page in pages],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", required=True)
    parser.add_argument("--semantic-map", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = validate_dist(args.dist, args.semantic_map)
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        pathlib.Path(args.output).write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
