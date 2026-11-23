# Logimu Shopping MCP

**Give Claude, ChatGPT, and any MCP client real shopping data.**

AI assistants are great at comparing products — and terrible at knowing today's price, what's actually in stock, and which "bestseller" is a relabeled generic. This MCP connector fixes that: your assistant gets **observed Amazon (US, UK, DE, CA, AU, FR, IT, ES, JP, MX, BR) and Walmart US data** — current prices, live stock, real ratings, price/BSR history, and ranked product shortlists — from a continuously refreshed warehouse of 17M+ tracked products.

**Free, no signup: 5 shopping searches per day. Every other tool needs a Logimu plan (from $19/month).**

```
https://api.logimu.com/mcp
```

## Quick start

| Client | How |
|---|---|
| **Claude** (claude.ai / desktop / mobile) | Settings → Connectors → Add custom connector → paste the URL above. **Authentication:** *Sign in now* if you have a Logimu plan (every tool, metered on your plan; OAuth, the connector never sees your key), or keep the pre-selected *No sign-in* for the free `shopping` tool only. **OAuth client:** keep *Use Claude's published identity*. Claude can't change this choice later: remove the connector and add it again. |
| **Claude Code** | `claude mcp add --transport http logimu https://api.logimu.com/mcp`, then `/mcp` to sign in when a paid tool asks, or `--header "Authorization: Bearer sk_live_…"` to pass the key directly |
| **ChatGPT** (developer mode), Cursor, VS Code, anything MCP | Add the same URL as a remote (Streamable HTTP) server. |

Then ask things like:

- *"Find me the best coffee maker under $80"* → ranked shortlists grouped by category or price tier
- *"Is ASIN B0BDHQSZCV a good buy right now?"* → price, stock, buy-box seller, 30-day price/stock changes, brand stats
- *"Well-rated dehumidifiers under $150 with 1,000+ reviews"* → structured warehouse filtering

## Tools

| Tool | Use when | Returns | Lane |
|---|---|---|---|
| `shopping` | "best X", "find me Y under $Z" — you want a shortlist | Ranked, grouped products (category or Budget/Mid/Premium tiers) with real ratings, prices, stock, `observed_at` stamps + brand facets, in ~100ms | Free: 1 of 5 daily, without `detail`; plan: 2 credits, 5 with `detail` |
| `product` | You have a specific ASIN/item — "good buy?", "price history?", "who sells this?" | Current snapshot + intelligence blocks: 30-day price/stock change events, all-seller offer table, brand stats, rating history and the rating breakdown by star with its per-day history from 2026-11-05 (percentages as Amazon prints them, counts approximate); full price, rank and buy-box histories with a key (included in the record), or `history_only` for the series alone (0.05 credit) | Paid plan: 0.5 credit from cache, 1 live |
| `search` | Filtered structured lists — price/rating/review/BSR/FBA filters, sorting | Up to 100 rows, across all 11 Amazon marketplaces plus Walmart US | Paid plan: 1 credit per 25 rows |
| `serp` | The live Amazon search-results page for a query, right now | Organic grid, sponsored and video blocks, refinements, pagination — a real fetch, seconds | API key: 1 credit per page fetched |
| `bestsellers` | What sells best in a category right now; Amazon's best-seller category tree | Up to 100 products in Amazon's rank order, the category's breadcrumb name and its subcategories; a root URL or a country alone returns the top-level categories. A real fetch (seconds), cached up to 30 min | API key: 1 credit per page of 50 (top 100 = 2), root list free |
| `offers` | Who sells a product right now, at what price; the cheapest new or used offer; the buy-box winner this minute | Every offer on Amazon's offers page (every page): seller and seller id, price, shipping, condition, buy box, FBA / FBM / Amazon, Prime, delivery promise and the seller's feedback, by ASIN or barcode. A real fetch (seconds); a no-offers answer is confirmed by a second, independent fetch | API key: 0.5 credit when an offer is listed; no offers, a miss or a failed fetch free |
| `deals` | What is on sale on Amazon right now: today's deals or lightning deals in a department, deals above a discount or under a price, coupon deals, deals ending today | Amazon's Today's Deals page, filtered as Amazon filters it (department, deal collection, % off, price, Prime Exclusive, rating, brand): deal and list price, % off, deal type and state, % claimed, the countdown end, coupon; plus the departments, collections and facets to filter by next and `filter_check` (did Amazon apply each filter). A real fetch (seconds a page), cached up to 15 min | API key: 1 credit per page fetched (up to 120 deals a page); an empty page or a failed fetch free |
| `seller` | A seller id — rating and feedback history, the storefront, the brands it was observed winning the buy box on, connected sellers | Stored profile (0.5) or live (1), +0.5 history; storefront pages 1 each; `brands` / `network` blocks +1 | Paid plan |
| `brand` | Who sells a brand, how contested / Amazon-dominated / FBA-heavy it is, its seller map | Brand dossier from observed buy-box data (1), +0.5 history, +1 per sellers page, +1 for the network of brands sharing sellers | Paid plan |
| `category` | How big / competitive / Amazon-dominated a category is, which brands lead it | Category landscape by id (1, +0.5 history); the name lookup is free | Paid plan |
| `market_lists` | Discover rather than look up — brands gaining or losing sellers, the biggest operators, categories ranked | 25 rows per page, 1 credit per page | Paid plan |
| `keywords` | Amazon's own autocomplete suggestion lists for a seed (positions within each list, first/last observed, marketplaces observed in, related vocabulary), `history` = each list's observation record, `compare` = the seed across marketplaces | 1 credit per lookup or compare, +0.5 with history | Paid plan |
| `keyword_rankings` | Page 1 of Amazon US search as last observed (about weekly) for head search terms: the organic order with product facts and each product's latest buy box, the sponsored units in the page HTML, the Overall Pick holder, who holds the page by brand and seller, and what changed since the previous observation; `history` = the weekly observations. Dated observations, never volume figures | 1 credit a keyword, +0.5 with history | Paid plan |
| `product_keywords` | Reverse ASIN on Amazon US: every observed keyword a product shows up for on page 1, with its rank; `asins` (up to 10) compares it with competitors and `gaps` keeps the keywords where they appear and it does not; `history` = its rank over time. Head search terms and page 1 only | 1 credit per 25 keywords per ASIN, +0.5 with history | Paid plan |
| `web_offers` | Where else a product is sold online (Target, Best Buy, eBay, brand stores ...): a price comparison or an arbitrage check for an ASIN, a Walmart item, a barcode or a brand + model | Offers read now from up to 8 shops' own product pages, each confirmed as the same item by barcode or by name, brand, model, size and pack, with price, availability and the match's confidence | Paid plan: 50 credits with a confirmed priced offer, 25 when no shop matched; failed searches free |
| `web_identify` | A barcode, supplier line or model number our records don't resolve: which product is it? | The product's identity (name, brand, model, size, pack) with its evidence, and the same product on Amazon and Walmart | Paid plan: 20 credits identified, 10 when the web names no one product; failed searches free |
| `web_product` | A product URL on a shop's own site (not Amazon or Walmart): its price and details, optionally matched to Amazon / Walmart | Name, brand, model, barcode, price, stock, condition, size, color, read now from the page | Paid plan: from 2 credits a page read; a page not read is free |
| `web_page` | What one web page says: a policy, a spec sheet, a press page | The page's visible text or its HTML, read now | Paid plan: 1 or 4 credits a page delivered; a page not read is free |
| `web_history` | How a product's price moved at other shops | One daily series per confirmed shop, from web offers searches and weekly re-reads | Paid plan: 2 credits when any point comes back |
| `track_product` | Watch a product's price, buy box, sellers or sales rank more often: every hour to every 7 days | Scheduled re-reads of the offers page (or the product page) with e-mail / webhook alerts; every read lands in the product's history | Paid plan: no credits, draws the plan's daily tracking allowance |
| `list_tracked` | What is being tracked, how much tracking room is left | Each tracking with its interval, last and next read, plus the plan's allowance | Paid plan: free |
| `batch` | More than a handful of ASINs, barcodes, terms, sellers or brands; a scheduled refresh; a CSV | Estimate, create, run and schedule (every 6 or 12 hours, daily, weekly, monthly) any endpoint over a list, then fetch the results | API key: estimate free; rows billed as the endpoint they run |
| `account` | Credits left, usage by endpoint, tracking room | The account's balance, plan, 30-day usage and tracking allowance | API key: free |

`tools/list` shows the whole catalog to every caller, and so does the stub. Without an account only `shopping` answers (5 searches a day); every other tool needs a Logimu account on a paid plan, by API key or by signing in when your client asks. Every derived figure is an observed count or share from Logimu's own data — never an estimate — and "observed since" is the data horizon, not a founding date. Keyword answers are Amazon's own suggestion ranking as observed — positions within one list, never volume figures; the observed page-1 positions of products are `keyword_rankings` and `product_keywords`.

Full REST API reference (same engine, same data): [api.logimu.com/docs](https://api.logimu.com/docs)

## Free lane and paid plans, honestly stated

| | Free (no signup) | Paid plan (API key) |
|---|---|---|
| Queries | 5 `shopping` searches / day | Credit-metered — subscriptions from $19/month, one-time credit packs, unconditional 14-day money-back |
| Data | `shopping`: ranked shortlists from the warehouse (fresh, timestamped), without `detail` | + `product` records with history, `search`, `shopping` `detail`, `mode=live` on-demand fetches, `serp`, `bestsellers`, `offers`, `deals`, seller profiles, brand / category intelligence and market lists, batch jobs on the REST API |
| Signup | None | [api.logimu.com](https://api.logimu.com) |

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
- API console & plans: [api.logimu.com](https://api.logimu.com)
- Docs: [api.logimu.com/docs](https://api.logimu.com/docs)
- Privacy: [logimu.com/privacy-policy](https://www.logimu.com/privacy-policy/) · Terms: [logimu.com/terms](https://www.logimu.com/terms/) · Refunds: [logimu.com/refund-policy](https://www.logimu.com/refund-policy/)
- Support: support@logimu.com

---

© 2026 Logimu · A service of CP Development doo · Not affiliated with Amazon or Walmart.
