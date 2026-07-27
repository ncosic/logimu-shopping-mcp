"""Introspection stub for the Logimu Shopping MCP.

The real server is HOSTED at https://api.logimu.com/mcp (Streamable HTTP,
free anonymous lane: 30 tool calls/day, no signup). This stdio stub exists so
directories that build-and-probe a repo (Glama et al.) can enumerate the tool
catalog without credentials; tools/call returns a pointer to the hosted
endpoint instead of executing. Stdlib only — no dependencies.
"""
from __future__ import annotations

import json
import sys

HOSTED = "https://api.logimu.com/mcp"

SERVER_INFO = {
    "name": "Logimu",
    "title": "Logimu — Amazon & Walmart Shopping Data",
    "version": "1.1.0",
    "websiteUrl": "https://api.logimu.com",
}

TOOLS = [
    {
        "name": "shopping",
        "description": (
            "Curated product search: a shopping keyword in, ranked product recommendations out "
            "(grouped by category or Budget/Mid-range/Premium price tier) in under ~100ms, in the "
            "marketplace's local currency, with real ratings, review counts, prices, stock, and an "
            "observed_at freshness stamp on every product. USE WHEN the user asks 'best X', 'find me "
            "a Y under $Z', or wants a shortlist to choose from. DON'T USE for a single known ASIN "
            "(use product) or for filtered dataset pulls (use search). RETURNS grouped product lists "
            "+ brand facets. detail=true (keyed accounts) attaches per-product intelligence "
            "(price/stock history, sellers, brand stats). COST on the free lane: 1 of 30 daily "
            "queries (detail unavailable); keyed: 2 credits, 10 with detail."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "q": {"type": "string", "description": "what to search for, e.g. 'coffee maker'"},
                "country": {"type": "string", "enum": ["us", "uk", "de", "ca", "au", "walmart"], "default": "us"},
                "group": {"type": "string", "enum": ["auto", "category", "price", "none"], "default": "auto"},
                "detail": {"type": "boolean", "default": False, "description": "attach per-product intelligence blocks (keyed accounts only)"},
            },
            "required": ["q"],
        },
        "annotations": {"title": "Shopping", "readOnlyHint": True},
    },
    {
        "name": "product",
        "description": (
            "THE single-product tool — one call returns the current snapshot (price, BSR, rating, "
            "buy-box seller, seller count, stock) PLUS intelligence blocks: observed_at freshness "
            "stamp, 30-day price/stock change events with the buy-box seller at each change, the "
            "current all-seller offer table, and brand stats. USE WHEN the user has a specific ASIN "
            "or product link and asks 'is this a good buy', 'did the price change', 'who sells this'. "
            "DON'T USE for discovery (use shopping). Marketplaces: us, uk, de, ca, au, walmart "
            "(numeric item ID; live mode is Amazon-only). COST on the free lane: 1 of 30 daily queries "
            "(cached data); keyed accounts can force mode=live for an on-demand scrape (~6s) on any "
            "Amazon marketplace."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "asin": {"type": "string", "description": "10-character ASIN (or numeric Walmart item ID with country=walmart)"},
                "country": {"type": "string", "enum": ["us", "uk", "de", "ca", "au", "walmart"], "default": "us"},
                "mode": {"type": "string", "enum": ["cache", "live", "auto"], "default": "auto"},
                "max_age_days": {"type": "integer", "default": 30},
            },
            "required": ["asin"],
        },
        "annotations": {"title": "Product", "readOnlyHint": True},
    },
    {
        "name": "search",
        "description": (
            "Warehouse filter search over 17M+ tracked Amazon (US/UK/DE/CA/AU) + Walmart products: keyword or "
            "brand anchor plus price/rating/review/BSR/FBA filters and sorting. USE WHEN the user "
            "wants a filtered structured list ('well-rated dehumidifiers under $150 with 1000+ "
            "reviews', 'everything by brand X sorted by BSR'). DON'T USE for 'best X' shopping "
            "advice (use shopping — it ranks and groups). RETURNS up to 25 rows on the free lane. "
            "COST: 1 of 30 daily free queries; keyed: 1 credit per 25 results."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "q": {"type": "string"},
                "brand": {"type": "string"},
                "marketplace": {"type": "string", "enum": ["amazon-us", "amazon-uk", "amazon-de", "amazon-ca", "amazon-au", "walmart"], "default": "amazon-us"},
                "price_min": {"type": "number"},
                "price_max": {"type": "number"},
                "rating_min": {"type": "number"},
                "reviews_min": {"type": "integer"},
                "sort": {"type": "string", "enum": ["bsr", "rating", "reviews", "price", "sales_estimate", "seller_count"], "default": "bsr"},
                "limit": {"type": "integer", "default": 25, "maximum": 100},
            },
        },
        "annotations": {"title": "Search", "readOnlyHint": True},
    },
]

POINTER = (
    "This is the introspection stub. The live server is hosted at "
    f"{HOSTED} — add it to your MCP client as a remote (Streamable HTTP) "
    "connector. Free, no signup: 30 queries/day. Unlimited + live scrapes: "
    "free API key with 2,500 credits at https://api.logimu.com"
)


def _reply(mid, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": mid}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        method, mid = msg.get("method"), msg.get("id")
        if method == "initialize":
            proto = (msg.get("params") or {}).get("protocolVersion") or "2025-06-18"
            _reply(mid, {
                "protocolVersion": proto,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
                "instructions": POINTER,
            })
        elif method == "tools/list":
            _reply(mid, {"tools": TOOLS})
        elif method == "tools/call":
            _reply(mid, {"content": [{"type": "text", "text": POINTER}], "isError": False})
        elif method == "ping":
            _reply(mid, {})
        elif mid is not None:
            _reply(mid, error={"code": -32601, "message": f"Method not found: {method}"})


if __name__ == "__main__":
    main()
