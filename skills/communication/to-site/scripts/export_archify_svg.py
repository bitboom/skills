#!/usr/bin/env python3
"""Export Archify's static diagram SVG without its HTML toolbar/runtime."""

import argparse
import pathlib
import re


STYLE = re.compile(r"<style[^>]*>([\s\S]*?)</style>", re.IGNORECASE)
SVG = re.compile(r"(<svg\b[\s\S]*?</svg>)", re.IGNORECASE)


def export_svg(html_path, output_path):
    source = pathlib.Path(html_path).read_text(encoding="utf-8")
    styles = STYLE.findall(source)
    svgs = SVG.findall(source)
    if len(svgs) != 1:
        raise ValueError("expected exactly one SVG in Archify HTML, found %d" % len(svgs))
    svg = svgs[0]
    if re.search(r"<script\b", svg, re.IGNORECASE):
        raise ValueError("SVG must not include scripts")
    style_text = ("\n".join(styles).rstrip() + "\nsvg { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }")
    root = re.match(r"<svg\b([^>]*)>", svg, re.IGNORECASE)
    if root is None:
        raise ValueError("SVG root is malformed")
    attributes = root.group(1)
    if "xmlns=" not in attributes:
        attributes += ' xmlns="http://www.w3.org/2000/svg"'
    if "data-theme=" not in attributes:
        attributes += ' data-theme="dark"'
    opening = "<svg%s>" % attributes
    svg = opening + "<style><![CDATA[" + style_text + "]]></style>" + svg[root.end():]
    output = pathlib.Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    export_svg(args.html, args.output)


if __name__ == "__main__":
    main()
