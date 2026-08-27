#!/usr/bin/env python3
"""
REGISTRAR · schema · the validator

**A schema nothing validates against is a document, not a contract.**

`patch.schema.json` had been in the tree since the beginning and **nothing in
the repository ever checked a file against it.** That is why two defects sat in
it undetected until an independent completion run reported them:

  · `gates/divergence.py` documented `derived_from` as the sanctioned way to
    justify a computed figure, while the schema set `additionalProperties:
    false` and did not declare it — **so a row using the gate's own escape hatch
    was schema-invalid.**
  · The schema admitted **no home for a declined target**, so holds had to ride
    in an annotation.

And a third, which explains the other two: **the worked example itself would
have failed strict validation**, because it teaches through `$note`. A schema
its own teaching example fails is a schema nobody was running.

All three are fixed. **This file is what stops them recurring** — law 9 again:
*a rule enforced only by asking people to follow it is not enforced.*

    python schema/validate.py <patch.json|patch.yml>
    python schema/validate.py --self          check the schema's own examples

ZERO DEPENDENCIES. Implements the subset of JSON Schema 2020-12 this contract
uses — `$ref`/`$defs`, type, required, properties, patternProperties,
additionalProperties, items, enum, const, pattern, minLength/maxLength,
minItems, minimum, format: date. **Not a general validator, and it says so**: a
general one would need a dependency, and "runs cold on clone" is a property this
repository does not trade away for coverage it does not need.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCHEMA = os.path.join(HERE, "patch.schema.json")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _resolve(node: dict, root: dict) -> dict:
    """Follow a local $ref. Only `#/...` is supported, and that is all this uses."""
    seen = 0
    while isinstance(node, dict) and "$ref" in node:
        ref = node["$ref"]
        if not ref.startswith("#/"):
            raise ValueError(f"only local refs are supported, got {ref!r}")
        cur = root
        for part in ref[2:].split("/"):
            cur = cur[part.replace("~1", "/").replace("~0", "~")]
        node = cur
        seen += 1
        if seen > 20:
            raise ValueError("$ref cycle")
    return node


def _type_ok(value, t: str) -> bool:
    if t == "object":
        return isinstance(value, dict)
    if t == "array":
        return isinstance(value, list)
    if t == "string":
        return isinstance(value, str)
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if t == "boolean":
        return isinstance(value, bool)
    if t == "null":
        return value is None
    return True


def validate(value, node: dict, root: dict, path: str = "") -> list[str]:
    """Returns a list of failures, each naming WHERE and WHAT. Empty means valid."""
    node = _resolve(node, root)
    out: list[str] = []
    at = path or "(root)"

    if "const" in node and value != node["const"]:
        out.append(f"{at}: must be {node['const']!r}, got {value!r}")
    if "enum" in node and value not in node["enum"]:
        out.append(f"{at}: must be one of {node['enum']}, got {value!r}")

    t = node.get("type")
    if t:
        types = t if isinstance(t, list) else [t]
        if not any(_type_ok(value, x) for x in types):
            out.append(f"{at}: expected {t}, got {type(value).__name__}")
            return out          # a wrong type makes every deeper check noise

    if isinstance(value, str):
        if "minLength" in node and len(value) < node["minLength"]:
            out.append(f"{at}: shorter than {node['minLength']} characters — {value!r}")
        if "maxLength" in node and len(value) > node["maxLength"]:
            out.append(f"{at}: longer than {node['maxLength']} characters")
        if "pattern" in node and not re.search(node["pattern"], value):
            out.append(f"{at}: {value!r} does not match {node['pattern']}")
        if node.get("format") == "date":
            try:
                _dt.date.fromisoformat(value)
            except ValueError:
                out.append(f"{at}: {value!r} is not an ISO date")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in node and value < node["minimum"]:
            out.append(f"{at}: {value} is below the minimum {node['minimum']}")

    if isinstance(value, list):
        if "minItems" in node and len(value) < node["minItems"]:
            out.append(f"{at}: needs at least {node['minItems']} item(s), has {len(value)}")
        item = node.get("items")
        if item:
            for i, x in enumerate(value):
                out += validate(x, item, root, f"{at}[{i}]")

    if isinstance(value, dict):
        for req in node.get("required", []):
            if req not in value:
                out.append(f"{at}: missing required field {req!r}")

        props = node.get("properties", {})
        patterns = node.get("patternProperties", {})
        for k, v in value.items():
            if k in props:
                out += validate(v, props[k], root, f"{at}.{k}" if path else k)
                continue
            matched = [p for p in patterns if re.search(p, k)]
            if matched:
                for p in matched:
                    out += validate(v, patterns[p], root, f"{at}.{k}" if path else k)
                continue
            if node.get("additionalProperties") is False:
                out.append(
                    f"{at}: {k!r} is not declared, and this object forbids extras"
                    + ("  (annotations must begin with `$`)" if patterns else ""))

    return out


def load(path: str):
    with open(path, encoding="utf-8") as fh:
        if path.endswith((".yml", ".yaml")):
            try:
                import yaml
            except ImportError:
                raise SystemExit("this input is YAML and pyyaml is absent — "
                                 "install pyyaml, or supply the JSON form")
            return yaml.safe_load(fh)
        return json.load(fh)


def check(path: str) -> int:
    with open(SCHEMA, encoding="utf-8") as fh:
        root = json.load(fh)
    doc = load(path)
    fails = validate(doc, root, root)

    print(f"schema · {os.path.relpath(path, ROOT)}")
    if not fails:
        rows = len(doc.get("rows") or [])
        holds = len(doc.get("holds") or doc.get("$holds") or [])
        print(f"  GREEN — valid against patch.schema.json  ({rows} rows, {holds} holds)")
        return 0
    print(f"  FAILED — {len(fails)} violation(s)")
    for f in fails[:20]:
        print(f"    {f}")
    if len(fails) > 20:
        print(f"    … and {len(fails) - 20} more")
    return 1


def self_check() -> int:
    """
    The examples this repository ships must validate against the contract it
    ships. **They did not, and nobody knew**, because nothing ran.
    """
    print("schema · the repository's own examples\n")
    targets = [
        os.path.join(ROOT, "examples", "worked", "northlake.patch.json"),
    ]
    rejected = os.path.join(ROOT, "examples", "worked", "rejected")
    if os.path.isdir(rejected):
        targets += [os.path.join(rejected, f) for f in sorted(os.listdir(rejected))
                    if f.endswith(".json")]

    bad = 0
    with open(SCHEMA, encoding="utf-8") as fh:
        root = json.load(fh)
    for t in targets:
        doc = load(t)
        fails = validate(doc, root, root)
        name = os.path.basename(t)
        is_adversarial = "rejected" in t
        if not fails:
            print(f"  ok      {name}")
        elif is_adversarial:
            # An adversarial fixture MAY be schema-invalid — that can be its defect.
            print(f"  (bad)   {name}  — {fails[0][:78]}")
        else:
            print(f"  FAILED  {name}")
            for f in fails[:6]:
                print(f"            {f}")
            bad += 1

    print()
    if bad:
        print(f"{bad} accepted example(s) do not validate against the schema this repository ships.")
        return 1
    print("Every accepted example validates. The contract and the teaching agree.")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or "--self" in a:
        raise SystemExit(self_check())
    raise SystemExit(check(a[0]))
