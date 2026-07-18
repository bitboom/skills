#!/usr/bin/env python3
"""Fail-closed semantic projection for a passed Point-to-site handoff."""

import argparse
import hashlib
import json
import pathlib
import re
import sys
from urllib.parse import urlparse


SOURCE_ID = re.compile(r"^S-[A-Za-z0-9_-]+$")
SEMANTIC_ID = re.compile(r"^[CNBE]-[A-Za-z0-9_-]+$")


def sha256_file(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unique_ids(records, kind, failures):
    seen = set()
    for record in records:
        value = record.get("id") if isinstance(record, dict) else None
        if not value:
            failures.append("%s has missing id" % kind)
            continue
        if value in seen:
            failures.append("duplicate %s id %s" % (kind, value))
        seen.add(value)
    return seen


def public_http_url(value):
    parsed = urlparse(value or "")
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def validate_projection(data):
    failures = []
    if not isinstance(data, dict):
        return {"passed": False, "failures": ["projection must be an object"]}
    if data.get("schema_version") != "to-site.input.v1":
        failures.append("schema_version must equal to-site.input.v1")
    manifest = data.get("source_manifest")
    if not isinstance(manifest, dict) or not re.fullmatch(r"[0-9a-f]{64}", manifest.get("point_sha256", "")):
        failures.append("source_manifest.point_sha256 must be a SHA-256")
    for required in ("title", "thesis"):
        if not isinstance(data.get(required), str) or not data[required].strip():
            failures.append("%s must be non-empty" % required)

    claims = data.get("claims")
    sources = data.get("sources")
    models = data.get("models")
    if not isinstance(claims, list) or not claims:
        failures.append("claims must be a non-empty list")
        claims = []
    if not isinstance(sources, list) or not sources:
        failures.append("sources must be a non-empty list")
        sources = []
    if not isinstance(models, dict):
        failures.append("models must be an object")
        models = {}

    claim_ids = unique_ids(claims, "claim", failures)
    source_ids = unique_ids(sources, "source", failures)
    for source in sources:
        source_id = source.get("id", "")
        if not SOURCE_ID.fullmatch(source_id):
            failures.append("source %s id is invalid" % source_id)
        if not isinstance(source.get("title"), str) or not source["title"].strip():
            failures.append("source %s has no title" % source_id)
        if not public_http_url(source.get("canonical_url")):
            failures.append("source %s canonical_url must be public http(s)" % source_id)
        if not isinstance(source.get("locator"), str) or not source["locator"].strip():
            failures.append("source %s has no locator" % source_id)

    for claim in claims:
        claim_id = claim.get("id", "")
        if not SEMANTIC_ID.fullmatch(claim_id):
            failures.append("claim %s id is invalid" % claim_id)
        for required in ("text", "evidence_status"):
            if not isinstance(claim.get(required), str) or not claim[required].strip():
                failures.append("claim %s has no %s" % (claim_id, required))
        for list_field in ("qualifiers", "proof_limits", "source_refs"):
            value = claim.get(list_field)
            if not isinstance(value, list) or not value:
                failures.append("claim %s has no %s" % (claim_id, list_field))
        for source_ref in claim.get("source_refs", []):
            if source_ref not in source_ids:
                failures.append("claim %s references unknown source %s" % (claim_id, source_ref))

    node_ids = set()
    for kind in ("nodes", "edges", "boundaries"):
        records = models.get(kind, [])
        if not isinstance(records, list):
            failures.append("models.%s must be a list" % kind)
            continue
        ids = unique_ids(records, "model %s" % kind[:-1], failures)
        if kind == "nodes":
            node_ids = ids
        for record in records:
            record_id = record.get("id", "")
            refs = record.get("source_refs")
            if not isinstance(refs, list) or not refs:
                failures.append("model %s %s has no source_refs" % (kind[:-1], record_id))
            for source_ref in refs or []:
                if source_ref not in source_ids:
                    failures.append("model %s %s references unknown source %s" % (kind[:-1], record_id, source_ref))
    for edge in models.get("edges", []) if isinstance(models.get("edges"), list) else []:
        for endpoint in ("from", "to"):
            if edge.get(endpoint) not in node_ids:
                failures.append("model edge %s has unknown %s node" % (edge.get("id", ""), endpoint))

    limits = data.get("does_not_prove")
    if not isinstance(limits, list) or not limits:
        failures.append("does_not_prove must be a non-empty list")
    return {"passed": not failures, "failures": failures, "claim_ids": sorted(claim_ids), "source_ids": sorted(source_ids)}


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_projection(data, output):
    result = validate_projection(data)
    if not result["passed"]:
        raise ValueError("; ".join(result["failures"]))
    output = pathlib.Path(output)
    output.mkdir(parents=True, exist_ok=True)
    claims = data["claims"]
    sources = data["sources"]
    models = data["models"]
    semantic_map = {
        "schema_version": "to-site.semantic-map.v1",
        "point_sha256": data["source_manifest"]["point_sha256"],
        "claims": {claim["id"]: claim["source_refs"] for claim in claims},
        "sources": [source["id"] for source in sources],
        "models": {
            kind: {record["id"]: record["source_refs"] for record in models.get(kind, [])}
            for kind in ("nodes", "edges", "boundaries")
        },
    }
    (output / "claims.generated.json").write_text(canonical_json(claims), encoding="utf-8")
    (output / "sources.generated.json").write_text(canonical_json(sources), encoding="utf-8")
    (output / "models.generated.json").write_text(canonical_json(models), encoding="utf-8")
    (output / "semantic-map.json").write_text(canonical_json(semantic_map), encoding="utf-8")
    (output / "site-content.json").write_text(canonical_json(data), encoding="utf-8")
    return semantic_map


def write_json_output(path, payload):
    destination = pathlib.Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(payload, encoding="utf-8")


def command_validate(args):
    data = json.loads(pathlib.Path(args.input).read_text(encoding="utf-8"))
    result = validate_projection(data)
    payload = canonical_json(result)
    if args.output:
        write_json_output(args.output, payload)
    else:
        sys.stdout.write(payload)
    return 0 if result["passed"] else 2


def command_project(args):
    data = json.loads(pathlib.Path(args.input).read_text(encoding="utf-8"))
    try:
        semantic_map = write_projection(data, args.output)
    except ValueError as error:
        result = {"passed": False, "failures": str(error).split("; ")}
        if args.report:
            write_json_output(args.report, canonical_json(result))
        else:
            sys.stdout.write(canonical_json(result))
        return 2
    result = {"passed": True, "semantic_map_sha256": hashlib.sha256(canonical_json(semantic_map).encode()).hexdigest()}
    if args.report:
        write_json_output(args.report, canonical_json(result))
    else:
        sys.stdout.write(canonical_json(result))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "project"):
        sub = commands.add_parser(name)
        sub.add_argument("--input", required=True)
        sub.add_argument("--output", required=name == "project")
        sub.add_argument("--report")
    args = parser.parse_args()
    return command_validate(args) if args.command == "validate" else command_project(args)


if __name__ == "__main__":
    raise SystemExit(main())
