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

# Tool catalog. CANONICAL and shared with the hosted server — the two MUST stay
# byte-identical: this stub is what MCP directories build and score, while real
# clients connect to the hosted endpoint and get the same catalog.
TOOLS = [
    {
        "name": "product",
        "description": (
            "Full dossier for ONE known product: its current snapshot plus its observed "
            "history. USE WHEN the user has a specific ASIN, Walmart item ID or product link "
            "and asks 'is this a good buy', 'has the price moved', 'who is selling this', 'is "
            "it in stock'. DON'T USE to discover products from a keyword (use shopping) or to "
            "pull a filtered list (use search). RETURNS current price, BSR, rating, review "
            "count, stock, buy-box seller and seller count, plus an observed_at freshness "
            "stamp, full price_history and stock_history back to first observation (with "
            "30-day convenience views), change events tagged with the buy-box seller at each "
            "change, the current all-seller offer table with 30-day buy-box days, the "
            "bought-past-month badge, and brand stats. For the ~17% of the catalog with no "
            "overall rank (media, books, niche items), bsr_leaf and bsr_leaf_category carry "
            "the best category rank instead. MARKETPLACES us, uk, de, ca, au, walmart. "
            "Walmart takes a numeric item ID and returns the intelligence blocks only (no "
            "live scrape). COST free lane 1 of 30 daily queries, cache only. Keyed: 0.5 "
            "credits from cache, 1 for a live scrape, +0.5 for the intelligence blocks, +0.5 "
            "each for bsr_history and offer_history. Misses and partial scrapes are never "
            "billed; a miss may return a hint (found on another marketplace, or retry with "
            "mode=live)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "asin": {
                    "type": "string",
                    "description": (
                        "10-character Amazon ASIN, or a numeric Walmart item ID when "
                        "country=walmart."
                    ),
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "walmart"],
                    "default": "us",
                    "description": (
                        "Marketplace to look the product up in. Amazon: us, uk, de, ca, au. "
                        "walmart = Walmart US."
                    ),
                },
                "mode": {
                    "type": "string",
                    "enum": ["cache", "live", "auto"],
                    "default": "auto",
                    "description": (
                        "cache = stored observation only; live = force an on-demand scrape "
                        "(Amazon only, takes a few seconds); auto = serve cache when fresher "
                        "than max_age_days, otherwise scrape. The free lane is always cache."
                    ),
                },
                "max_age_days": {
                    "type": "integer",
                    "default": 30,
                    "description": (
                        "How old a cached observation may be before mode=auto triggers a live "
                        "scrape."
                    ),
                },
                "offer_history": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Attach the buy-box owner timeline and per-seller daily price series "
                        "(US buy-box depth back to Dec 2024). Amazon marketplaces only. +0.5 "
                        "credits when data is returned."
                    ),
                },
                "bsr_history": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Attach the full per-category BSR rank history (era-tagged daily "
                        "points back to Oct 2023 for US; legacy top-100 segments are flagged "
                        "censored). Amazon marketplaces only. +0.5 credits when data is "
                        "returned."
                    ),
                },
            },
            "required": ["asin"],
        },
        "annotations": {"title": "Product", "readOnlyHint": True, "openWorldHint": True},
    },
    {
        "name": "shopping",
        "description": (
            "Curated product discovery: a shopping keyword in, a ranked and grouped shortlist "
            "out, in under ~100ms. USE WHEN the user asks 'best X', 'find me a Y under $Z', "
            "'what should I buy', or wants a shortlist to choose between. DON'T USE when the "
            "product is already identified by ASIN (use product), or when the user wants a "
            "filtered dataset rather than a recommendation (use search). RETURNS ranked "
            "products grouped either by category or by Budget/Mid-range/Premium price tier "
            "(chosen algorithmically, or forced with group), each carrying title, price in "
            "the marketplace's local currency, rating, review count, stock and an observed_at "
            "freshness stamp, plus brand facets. Ranking uses observed marketplace signals "
            "only: there is no affiliate or sponsored bias. A bare ASIN in q returns exactly "
            "that product. MARKETPLACES us, uk, de, ca, au, walmart. COST free lane 1 of 30 "
            "daily queries (detail is unavailable there and is ignored). Keyed: 2 credits, or "
            "5 with detail=true. Empty result sets are never billed."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": (
                        "What to search for, e.g. 'coffee maker'. A bare ASIN returns exactly "
                        "that product."
                    ),
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "walmart"],
                    "default": "us",
                    "description": (
                        "Marketplace to search. Amazon: us, uk, de, ca, au. walmart = Walmart "
                        "US. Prices are returned in that marketplace's local currency."
                    ),
                },
                "group": {
                    "type": "string",
                    "enum": ["auto", "category", "price", "none"],
                    "default": "auto",
                    "description": (
                        "How to group the shortlist. auto = choose category or price tiers "
                        "automatically; category = group by product category; price = group "
                        "into Budget/Mid-range/Premium; none = one flat ranked list."
                    ),
                },
                "detail": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Attach per-product intelligence to every product returned (30-day "
                        "price and stock change events, full stock history and state, "
                        "bought-past-month badge, current sellers). Keyed accounts only. 5 "
                        "credits per query instead of 2."
                    ),
                },
            },
            "required": ["q"],
        },
        "annotations": {"title": "Shopping", "readOnlyHint": True, "openWorldHint": False},
    },
    {
        "name": "search",
        "description": (
            "Filtered query over the tracked-product warehouse (17M+ Amazon and Walmart "
            "products). USE WHEN the user wants a structured list matching explicit criteria: "
            "'well-rated dehumidifiers under $150 with 1000+ reviews', 'everything by brand X "
            "sorted by BSR', 'FBA products in this category'. DON'T USE for 'best X' buying "
            "advice (use shopping, which ranks and groups), or for a single known product "
            "(use product). RETURNS a flat list of matching products with title, brand, "
            "price, rating, review count, BSR, seller count and marketplace, ordered by the "
            "sort field. Requires an anchor: pass q or brand. COVERAGE the continuously "
            "tracked BSR product universe, not the entire Amazon catalog. COST free lane 1 of "
            "30 daily queries, capped at 25 rows. Keyed: 1 credit per 25 rows returned. Empty "
            "result sets are never billed."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": (
                        "Keyword matched against the product title. Acts as the anchor when "
                        "brand is not given."
                    ),
                },
                "brand": {
                    "type": "string",
                    "description": "Exact brand name. Acts as the anchor when q is not given.",
                },
                "seller": {
                    "type": "string",
                    "description": (
                        "Restrict to products this seller has been observed offering."
                    ),
                },
                "category": {
                    "type": "string",
                    "description": "Restrict to a single product category.",
                },
                "marketplace": {
                    "type": "string",
                    "enum": [
                        "amazon-us",
                        "amazon-uk",
                        "amazon-de",
                        "amazon-ca",
                        "amazon-au",
                        "walmart",
                    ],
                    "default": "amazon-us",
                    "description": "Which tracked marketplace to query.",
                },
                "price_min": {
                    "type": "number",
                    "description": "Minimum current price, in the marketplace's local currency.",
                },
                "price_max": {
                    "type": "number",
                    "description": "Maximum current price, in the marketplace's local currency.",
                },
                "rating_min": {
                    "type": "number",
                    "description": "Minimum star rating, on a 0-5 scale.",
                },
                "reviews_min": {"type": "integer", "description": "Minimum number of reviews."},
                "bsr_min": {
                    "type": "integer",
                    "description": (
                        "Minimum Best Sellers Rank. Lower BSR means stronger sales, so this "
                        "excludes the best sellers."
                    ),
                },
                "bsr_max": {
                    "type": "integer",
                    "description": (
                        "Maximum Best Sellers Rank. Use this to keep only strong sellers."
                    ),
                },
                "fba": {
                    "type": "boolean",
                    "description": (
                        "true = only Fulfilled by Amazon offers, false = only "
                        "merchant-fulfilled. Omit to include both."
                    ),
                },
                "sort": {
                    "type": "string",
                    "enum": [
                        "bsr",
                        "rating",
                        "reviews",
                        "price",
                        "sales_estimate",
                        "seller_count",
                    ],
                    "default": "bsr",
                    "description": (
                        "Field to order results by. bsr sorts ascending (best sellers first); "
                        "the others sort descending."
                    ),
                },
                "max_per_category": {
                    "type": "integer",
                    "description": (
                        "Cap how many results may come from any one category, to spread "
                        "results across categories."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "default": 50,
                    "maximum": 100,
                    "description": (
                        "Maximum rows to return (up to 100). The free lane caps this at 25."
                    ),
                },
            },
        },
        "annotations": {"title": "Search", "readOnlyHint": True, "openWorldHint": False},
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
