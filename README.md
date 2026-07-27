# Logimu Shopping MCP

**Give Claude, ChatGPT, and any MCP client real shopping data.**

AI assistants are great at comparing products — and terrible at knowing today's price, what's actually in stock, and which "bestseller" is a relabeled generic. This MCP connector fixes that: your assistant gets **observed Amazon (US, UK, DE, CA, AU) and Walmart data** — current prices, live stock, real ratings, price/BSR history, and ranked product shortlists — from a continuously refreshed warehouse of 17M+ tracked products.

**Free, no signup: 30 queries per day.**

```
https://api.logimu.com/mcp
```

## Quick start

| Client | How |
|---|---|
| **Claude** (claude.ai / desktop) | Settings → Connectors → Add custom connector → paste the URL above. No key needed. |
| **Claude Code** | `claude mcp add --transport http logimu https://api.logimu.com/mcp` |
| **ChatGPT** (developer mode), Cursor, VS Code, anything MCP | Add the same URL as a remote (Streamable HTTP) server. |

Then ask things like:

- *"Find me the best coffee maker under $80"* → ranked shortlists grouped by category or price tier
- *"Is ASIN B0BDHQSZCV a good buy right now?"* → price, stock, buy-box seller, 30-day price/stock changes, brand stats
- *"Well-rated dehumidifiers under $150 with 1,000+ reviews"* → structured warehouse filtering

## Tools

| Tool | Use when | Returns | Free-lane cost |
|---|---|---|---|
| `shopping` | "best X", "find me Y under $Z" — you want a shortlist | Ranked, grouped products (category or Budget/Mid/Premium tiers) with real ratings, prices, stock, `observed_at` stamps + brand facets, in ~100ms | 1 of 30 daily |
| `product` | You have a specific ASIN/item — "good buy?", "price history?", "who sells this?" | Current snapshot + intelligence blocks: 30-day price/stock change events, all-seller offer table, brand stats | 1 of 30 daily |
| `search` | Filtered structured lists — price/rating/review/BSR/FBA filters, sorting | Up to 25 rows on the free lane from 17M+ tracked products across all six marketplaces | 1 of 30 daily |

Full REST API reference (same engine, same data): [api.logimu.com/docs](https://api.logimu.com/docs)

## Free tier, honestly stated

| | Free (no signup) | With a free API key |
|---|---|---|
| Queries | 30 / day | 2,500 free credits, then flat credits from $0.15 per 1,000 |
| Data | Full warehouse, cached (fresh, timestamped) | Warehouse + `mode=live` on-demand scrape (~6s, any Amazon marketplace) + shopping `detail` mode |
| Signup | None | Email only, no card — [api.logimu.com](https://api.logimu.com) |

- Every record carries an `observed_at` timestamp — data is **observed** from our warehouse, not a live retailer feed.
- We have **no affiliate or seller relationship** with anything the tools return. Nothing is ranked because someone paid for it.
- Failed or empty requests are never billed, on any tier.

## What's in this repo

The live server is **hosted** — this repo carries the tool catalog, an introspection-only stdio stub (`logimu-mcp-stub`) so directory build harnesses can enumerate the tools without credentials, and the listing metadata. `tools/call` on the stub returns a pointer to the hosted endpoint.

```bash
pip install .
logimu-mcp-stub   # stdio MCP: initialize / tools/list work; tools/call points to the hosted server
```

## Links

- Product page: [logimu.com/shopping-mcp](https://www.logimu.com/shopping-mcp/)
- API console & free credits: [api.logimu.com](https://api.logimu.com)
- Docs: [api.logimu.com/docs](https://api.logimu.com/docs)
- Privacy: [api.logimu.com/privacy](https://api.logimu.com/privacy) · Terms: [api.logimu.com/terms](https://api.logimu.com/terms)
- Support: support@logimu.com

---

© 2026 Logimu · A service of CP Development doo · Not affiliated with Amazon or Walmart.
