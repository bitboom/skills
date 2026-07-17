#!/usr/bin/env python3
"""Render a PPTX into portable To Deck QA artifacts.

The manifest deliberately stores slide paths relative to itself so a review
trail can be copied or extracted without retaining the build machine path.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import zipfile
from typing import Any, Iterable


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_version(command: str) -> str:
    for flag in ("--version", "-v"):
        result = subprocess.run(
            [command, flag], check=False, capture_output=True, text=True
        )
        text = (result.stdout or result.stderr).strip()
        if result.returncode == 0 and text:
            return text.splitlines()[0]
    raise RuntimeError(f"cannot determine version for {command}")


def require_command(command: str) -> str:
    resolved = shutil.which(command)
    if resolved is None:
        raise RuntimeError(
            f"required command is missing: {command}. "
            "Install the configured PPTX QA toolchain before rendering."
        )
    return resolved


def relative_path(path: Path, base: Path) -> str:
    return Path(os.path.relpath(path.resolve(), base.resolve())).as_posix()


def build_manifest(
    *,
    manifest_path: Path,
    rendered_slides: Iterable[Path],
    slide_size: tuple[int, int],
    toolchain: dict[str, str],
    producer: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    """Build the schema-v2 manifest used by ``slide-gate``.

    Paths are deliberately relative to the manifest directory.  Callers must
    create output in the package tree before calling this function.
    """
    base = manifest_path.resolve().parent
    slides = list(rendered_slides)
    if not slides:
        raise ValueError("at least one rendered slide is required")
    width, height = slide_size
    if width <= 0 or height <= 0:
        raise ValueError("rendered slide dimensions must be positive")
    entries = []
    for image in slides:
        if not image.is_file():
            raise ValueError(f"rendered slide is missing: {image}")
        relative = relative_path(image, base)
        relative_path_value = Path(relative)
        if relative_path_value.is_absolute() or ".." in relative_path_value.parts:
            raise ValueError("rendered slides must stay inside the manifest directory")
        entries.append({
            "path": relative,
            "width": width,
            "height": height,
            "sha256": sha256(image),
        })
    required_toolchain = {"renderer", "renderer_version", "command", "environment"}
    missing_toolchain = sorted(
        name for name in required_toolchain
        if not isinstance(toolchain.get(name), str) or not toolchain[name].strip()
    )
    if missing_toolchain:
        raise ValueError("toolchain fields are missing: " + ", ".join(missing_toolchain))
    kind = producer.get("kind")
    command = producer.get("command")
    if kind not in {"manual", "script"} or not isinstance(command, str) or not command.strip():
        raise ValueError("producer must declare kind (manual or script) and command")
    if kind == "script":
        for name in ("source_path", "source_sha256"):
            if not isinstance(producer.get(name), str) or not producer[name].strip():
                raise ValueError(f"script producer is missing {name}")
    return {
        "schema_version": 2,
        "renderer": toolchain["renderer"],
        "renderer_version": toolchain["renderer_version"],
        "command": toolchain["command"],
        "generated_at": generated_at,
        "toolchain": toolchain,
        "producer": producer,
        "slide_count": len(entries),
        "slides": entries,
    }


def image_dimensions(path: Path) -> tuple[int, int]:
    signature = path.read_bytes()[:24]
    if signature[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"rendered file is not a PNG: {path}")
    return int.from_bytes(signature[16:20], "big"), int.from_bytes(signature[20:24], "big")


def producer_metadata(args: argparse.Namespace, manifest_path: Path) -> dict[str, Any]:
    producer: dict[str, Any] = {"kind": args.producer_kind, "command": args.producer_command}
    if args.producer_kind == "script":
        if not args.producer_source:
            raise RuntimeError("--producer-source is required when --producer-kind=script")
        source = Path(args.producer_source).resolve()
        if not source.is_file():
            raise RuntimeError(f"producer source is missing: {source}")
        source_relative = Path(relative_path(source, manifest_path.parent))
        if source_relative.is_absolute() or ".." in source_relative.parts:
            raise RuntimeError("producer source must live inside the manifest directory")
        producer["source_path"] = source_relative.as_posix()
        producer["source_sha256"] = sha256(source)
        if args.producer_lockfile:
            lockfile = Path(args.producer_lockfile).resolve()
            if not lockfile.is_file():
                raise RuntimeError(f"producer lockfile is missing: {lockfile}")
            lockfile_relative = Path(relative_path(lockfile, manifest_path.parent))
            if lockfile_relative.is_absolute() or ".." in lockfile_relative.parts:
                raise RuntimeError("producer lockfile must live inside the manifest directory")
            producer["lockfile_path"] = lockfile_relative.as_posix()
            producer["lockfile_sha256"] = sha256(lockfile)
    return producer


def pptx_slide_count(path: Path) -> int:
    try:
        with zipfile.ZipFile(path) as deck:
            slides = [
                name for name in deck.namelist()
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
            ]
    except (OSError, zipfile.BadZipFile) as exc:
        raise RuntimeError(f"invalid PPTX {path}: {exc}") from exc
    if not slides:
        raise RuntimeError(f"PPTX has no slide XML entries: {path}")
    return len(slides)


def rendered_slide_paths(output_dir: Path) -> list[Path]:
    numbered = []
    for path in output_dir.glob("slide-*.png"):
        match = re.fullmatch(r"slide-(\d+)\.png", path.name)
        if match:
            numbered.append((int(match.group(1)), path))
    numbered.sort(key=lambda row: row[0])
    expected = list(range(1, len(numbered) + 1))
    numbers = [number for number, _ in numbered]
    if numbers != expected:
        raise RuntimeError("Poppler output slide names are not a contiguous 1..N sequence")
    return [path for _, path in numbered]


def remove_stale_render_outputs(output_dir: Path, pdf: Path, text_output: Path, manifest_path: Path) -> None:
    for image in output_dir.glob("slide-*.png"):
        image.unlink()
    for artifact in (pdf, text_output, manifest_path):
        if artifact.is_file():
            artifact.unlink()


def run(args: argparse.Namespace) -> int:
    deck = Path(args.deck).resolve()
    manifest_path = Path(args.manifest).resolve()
    output_dir = Path(args.output_dir).resolve()
    text_output = Path(args.text_output).resolve() if args.text_output else output_dir / "deck-text.md"
    if not deck.is_file():
        raise RuntimeError(f"PPTX is missing: {deck}")
    if deck.suffix.lower() != ".pptx":
        raise RuntimeError(f"expected a .pptx deck: {deck}")
    if not isinstance(args.dpi, int) or args.dpi <= 0:
        raise RuntimeError("--dpi must be a positive integer")
    expected_slide_count = pptx_slide_count(deck)
    soffice = require_command(args.soffice)
    pdftoppm = require_command(args.pdftoppm)
    markitdown = require_command(args.markitdown)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    text_output.parent.mkdir(parents=True, exist_ok=True)
    pdf = output_dir / f"{deck.stem}.pdf"
    remove_stale_render_outputs(output_dir, pdf, text_output, manifest_path)

    convert = subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(output_dir), str(deck)],
        check=False, capture_output=True, text=True,
    )
    if convert.returncode != 0:
        raise RuntimeError("LibreOffice conversion failed:\n" + (convert.stdout + convert.stderr).strip())
    if not pdf.is_file():
        raise RuntimeError(f"LibreOffice did not create expected PDF: {pdf}")
    prefix = output_dir / "slide"
    rasterize = subprocess.run(
        [pdftoppm, "-png", "-r", str(args.dpi), str(pdf), str(prefix)],
        check=False, capture_output=True, text=True,
    )
    if rasterize.returncode != 0:
        raise RuntimeError("Poppler rendering failed:\n" + (rasterize.stdout + rasterize.stderr).strip())
    slides = rendered_slide_paths(output_dir)
    if not slides:
        raise RuntimeError("Poppler did not create any slide PNGs")
    if len(slides) != expected_slide_count:
        raise RuntimeError(
            f"Poppler rendered {len(slides)} slides but PPTX declares {expected_slide_count}"
        )
    extract = subprocess.run(
        [markitdown, str(deck), "-o", str(text_output)],
        check=False, capture_output=True, text=True,
    )
    if extract.returncode != 0:
        raise RuntimeError("MarkItDown extraction failed:\n" + (extract.stdout + extract.stderr).strip())
    if not text_output.is_file() or not text_output.read_text(encoding="utf-8").strip():
        raise RuntimeError(f"MarkItDown did not create non-empty text output: {text_output}")

    dimensions = image_dimensions(slides[0])
    if any(image_dimensions(path) != dimensions for path in slides[1:]):
        raise RuntimeError("rendered slides do not share one pixel size")
    toolchain = {
        "renderer": Path(soffice).name,
        "renderer_version": command_version(soffice),
        "command": f"{Path(soffice).name} --headless --convert-to pdf",
        "environment": f"{platform.system()} {platform.release()} {platform.machine()}",
        "pdf_rasterizer": Path(pdftoppm).name,
        "pdf_rasterizer_version": command_version(pdftoppm),
        "text_extractor": Path(markitdown).name,
        "text_extractor_version": command_version(markitdown),
        "dpi": str(args.dpi),
    }
    manifest = build_manifest(
        manifest_path=manifest_path,
        rendered_slides=slides,
        slide_size=dimensions,
        toolchain=toolchain,
        producer=producer_metadata(args, manifest_path),
        generated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    )
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifest": str(manifest_path), "pdf": str(pdf), "text": str(text_output),
        "slides": [str(path) for path in slides],
    }, ensure_ascii=False))
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--deck", required=True)
    value.add_argument("--manifest", required=True)
    value.add_argument("--output-dir", required=True)
    value.add_argument("--text-output")
    value.add_argument("--dpi", type=int, default=180)
    value.add_argument("--soffice", default="soffice")
    value.add_argument("--pdftoppm", default="pdftoppm")
    value.add_argument("--markitdown", default="markitdown")
    value.add_argument("--producer-kind", choices=("manual", "script"), default="manual")
    value.add_argument("--producer-command", default="manual PPTX authoring")
    value.add_argument("--producer-source")
    value.add_argument("--producer-lockfile")
    return value


def main() -> int:
    try:
        return run(parser().parse_args())
    except RuntimeError as error:
        print(f"render-deck: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
