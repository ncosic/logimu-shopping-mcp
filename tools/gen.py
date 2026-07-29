"""Render canonical_tools.TOOLS into both consuming files, so they cannot drift.

Usage: python3 gen.py <mcp.py path> <stub.py path>
Splices the generated literal over the existing _TOOLS / TOOLS block in each file.
Idempotent: re-running produces a byte-identical result.
"""
from __future__ import annotations

import re
import sys
import textwrap

from canonical_tools import TOOLS

WRAP_AT = 96


def q(s: str) -> str:
    """Double-quoted literal to match house style; fall back to repr if the text has a quote."""
    if '"' in s:
        return repr(s)
    import json
    return json.dumps(s, ensure_ascii=False)


def _flat(value) -> str:
    """One-line rendering of a small container, using double-quoted strings."""
    if isinstance(value, str):
        return q(value)
    if isinstance(value, list):
        return "[" + ", ".join(_flat(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{q(k)}: {_flat(v)}" for k, v in value.items()) + "}"
    return repr(value)


def render(value, indent: int, *, key_prefix: str = "") -> str:
    """Render a JSON-ish Python value as readable Python source."""
    pad = " " * indent
    if isinstance(value, str):
        head = pad + key_prefix
        # short strings stay on one line
        if len(head) + len(q(value)) <= WRAP_AT:
            return head + q(value)
        inner_pad = " " * (indent + 4)
        chunks = textwrap.wrap(value, width=WRAP_AT - len(inner_pad) - 4,
                               break_long_words=False, break_on_hyphens=False)
        # keep a trailing space on every chunk but the last so concatenation reads correctly
        parts = [q(c + " ") if i < len(chunks) - 1 else q(c)
                 for i, c in enumerate(chunks)]
        body = ("\n" + inner_pad).join(parts)
        return head + "(\n" + inner_pad + body + "\n" + pad + ")"
    if isinstance(value, bool) or value is None or isinstance(value, (int, float)):
        return pad + key_prefix + repr(value)
    if isinstance(value, list):
        head = pad + key_prefix
        flat = head + _flat(value)
        if len(flat) <= WRAP_AT and not any(isinstance(v, (dict, list)) for v in value):
            return flat
        items = ",\n".join(render(v, indent + 4) for v in value)
        return head + "[\n" + items + ",\n" + pad + "]"
    if isinstance(value, dict):
        head = pad + key_prefix
        flat = head + _flat(value)
        if len(flat) <= WRAP_AT and not any(isinstance(v, (dict, list, str)) and
                                            (isinstance(v, (dict, list)) or len(repr(v)) > 40)
                                            for v in value.values()):
            return flat
        items = ",\n".join(render(v, indent + 4, key_prefix=q(k) + ": ")
                           for k, v in value.items())
        return head + "{\n" + items + ",\n" + pad + "}"
    raise TypeError(f"unsupported: {type(value)!r}")


HEADER = (
    "# Tool catalog. CANONICAL and shared with the public introspection stub\n"
    "# (github.com/ncosic/logimu-shopping-mcp, logimu_mcp/stub.py) — the two MUST stay\n"
    "# byte-identical: directories (Glama et al.) score the stub, real clients get this one.\n"
    "# Description shape is deliberate (purpose / USE WHEN / DON'T USE / RETURNS /\n"
    "# MARKETPLACES / COST, every parameter described) and credit figures are verified\n"
    "# against _dispatch + routes.compute_unified_product. NEVER hand-edit this block:\n"
    "# edit tools/canonical_tools.py in the stub repo and re-run tools/gen.py.\n"
    "# Naming (2026-07-23) matches the REST surface: shopping=answers, search=data, product=one item.\n"
)

STUB_HEADER = (
    "# Tool catalog. CANONICAL and shared with the hosted server — the two MUST stay\n"
    "# byte-identical: this stub is what MCP directories build and score, while real\n"
    "# clients connect to the hosted endpoint and get the same catalog.\n"
    "# NEVER hand-edit this block: edit tools/canonical_tools.py and re-run tools/gen.py.\n"
)


def splice(path: str, var: str, header: str) -> bool:
    src = open(path, encoding="utf-8").read()
    literal = render(TOOLS, 0)
    block = header + f"{var} = " + literal.lstrip() + "\n"
    pattern = re.compile(rf"(?:^#[^\n]*\n)*^{re.escape(var)} = \[.*?^\]\n", re.S | re.M)
    if not pattern.search(src):
        raise SystemExit(f"FAIL: could not locate the {var} block in {path}")
    new = pattern.sub(lambda _m: block, src, count=1)
    if new == src:
        print(f"  unchanged: {path}")
        return False
    open(path, "w", encoding="utf-8").write(new)
    print(f"  written:   {path}")
    return True


if __name__ == "__main__":
    mcp_path, stub_path = sys.argv[1], sys.argv[2]
    splice(mcp_path, "_TOOLS", HEADER)
    splice(stub_path, "TOOLS", STUB_HEADER)
