"""Canonical Logimu MCP tool catalog.

SINGLE SOURCE OF TRUTH for the tool definitions served by BOTH:
  - the live hosted server : nick/brand-intel  api/public_api/mcp.py   (_TOOLS)
  - the introspection stub : ncosic/logimu-shopping-mcp  logimu_mcp/stub.py  (TOOLS)

The two live in different repos, so the definitions are duplicated. This file
generates both so they cannot drift. Re-run gen.py after any edit here.

Description shape is deliberate (Glama TDQS scores 6 dimensions):
  <purpose> / USE WHEN / DON'T USE / RETURNS / MARKETPLACES / COST
and EVERY parameter carries a description (Parameter Semantics, 15%).
Costs below are verified against the code, not the docs:
  product : routes.compute_unified_product -> base 0 partial / 0.5 cache / 1.0 live,
            +0.5 intelligence, +0.5 each history flag; 404 unbilled
  shopping: mcp._dispatch -> 2 credits, 5 with detail; 0 when total == 0
  search  : mcp._dispatch -> ceil(rows/25) credits; 0 when no rows
Free lane (mcp._call_anon): 30 calls/client/UTC day, mode=live downgraded to auto,
detail forced False, search limit clamped to 25, never billed.
"""

TOOLS = [
    {
        "name": "product",
        "description": (
            "Full dossier for ONE known product: its current snapshot plus its observed history. "
            "USE WHEN the user has a specific ASIN, Walmart item ID, product link, or a "
            "product_id returned by shopping or search, and asks about price history, "
            "historical prices, price changes, 30-day history, stock history, seller "
            "history, buy-box history, historical analysis, 'analyse this product', "
            "'is this a good buy', 'has the price moved/dropped', 'who is selling this', "
            "'is it in stock'. This is the ONLY tool that returns history: shopping and "
            "search return current values, so any historical question about a product they "
            "listed comes here. "
            "DON'T USE to discover products from a keyword (use shopping) or to pull a filtered "
            "list (use search). "
            "RETURNS current price, BSR, rating, review count, stock, buy-box seller and seller "
            "count, plus an observed_at freshness stamp, full price_history and stock_history back "
            "to first observation (keyed; the free lane carries the 30-day views), change events tagged with the "
            "buy-box seller at each change, the current all-seller offer table with 30-day buy-box "
            "days, the bought-past-month badge (measured aggregate buyer behavior, not an estimate), and "
            "brand stats. For the ~17% of the catalog with "
            "no overall rank (media, books, niche items), bsr_leaf and bsr_leaf_category carry the "
            "best category rank instead. "
            "Every response carries a data_source field naming the marketplace the numbers were "
            "observed on (e.g. 'amazon US marketplace \u2014 observed listings') \u2014 attribute prices to "
            "that source when presenting them; they are marketplace listings, not manufacturer or "
            "site-wide prices. "
            "MARKETPLACES us, uk, de, ca, au, fr, it, es, jp, mx, br, walmart. Walmart takes a numeric item ID and returns "
            "the intelligence blocks only (no live scrape). "
            "COST free lane 1 of 30 daily queries, cache only, and returns the snapshot + 30-day "
            "views (the full history streams, bsr_history, offer_history and live scrapes need a "
            "free API key — the response's locked block lists exactly what a key unlocks). Keyed: "
            "0.5 credits from cache, 1 for "
            "a live scrape, +0.5 for the intelligence blocks, +0.5 each for bsr_history and "
            "offer_history. Misses and partial scrapes are never billed; a miss may return a hint "
            "(found on another marketplace, or retry with mode=live)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "asin": {
                    "type": "string",
                    "description": "10-character Amazon ASIN, or a numeric Walmart item ID when country=walmart.",
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "fr", "it", "es", "jp", "mx", "br", "walmart"],
                    "default": "us",
                    "description": (
                        "Marketplace to look the product up in. Amazon: us, uk, de, ca, au. "
                        "walmart = Walmart US (United States only). Pick the marketplace matching "
                        "the user's country or locale when known (a German user -> de, a Canadian "
                        "user -> ca); default us."
                    ),
                },
                "mode": {
                    "type": "string",
                    "enum": ["cache", "live", "auto"],
                    "default": "auto",
                    "description": (
                        "cache = stored observation only; live = force an on-demand scrape (Amazon "
                        "only, takes a few seconds); auto = serve cache when fresher than "
                        "max_age_days, otherwise scrape. The no-signup free lane is cache-only: "
                        "mode=live returns an error asking for a free API key (do not offer a live "
                        "scrape to a keyless caller); with a key, live/auto scrape normally."
                    ),
                },
                "max_age_days": {
                    "type": "integer",
                    "default": 30,
                    "description": "How old a cached observation may be before mode=auto triggers a live scrape.",
                },
                "offer_history": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Attach the buy-box owner timeline and per-seller daily price series (US "
                        "buy-box depth back to Dec 2024). Amazon marketplaces only, API key "
                        "required (free key works). +0.5 credits when data is returned."
                    ),
                },
                "bsr_history": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Attach the full per-category BSR rank history (era-tagged daily points "
                        "back to Oct 2023 for US; legacy top-100 segments are flagged censored). "
                        "Amazon marketplaces only, API key required (free key works). +0.5 credits "
                        "when data is returned."
                    ),
                },
            },
            "required": ["asin"],
        },
        "annotations": {"title": "Product", "readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
    },
    {
        "name": "shopping",
        "description": (
            "Curated product discovery: a shopping keyword in, a ranked and grouped shortlist out, "
            "in under ~100ms. "
            "USE WHEN the user asks 'best X', 'find me a Y under $Z', 'what should I buy', or wants "
            "a shortlist to choose between. "
            "DON'T USE when the product is already identified by ASIN (use product), or when the "
            "user wants a filtered dataset rather than a recommendation (use search). "
            "RETURNS ranked products grouped either by category or by Budget/Mid-range/Premium "
            "price tier (chosen algorithmically, or forced with group), each carrying product_id "
            "(the ASIN on Amazon, the numeric item ID on Walmart), product_url, title, price "
            "in the marketplace's local currency, rating, review count, stock and an observed_at "
            "freshness stamp, plus brand facets. Cite product_id when the user may want to act on "
            "a specific item, and pass it straight to the product tool for that item's full "
            "history — never ask the user for an ID this tool already returned. "
            "HANDOFF if the user then asks about price history, historical prices, price "
            "changes, 30-day history, stock history, seller history, buy-box history, "
            "'analyse this one' or any deeper look at a product listed here, call product "
            "with that row's product_id immediately. EXAMPLE user: 'best electric "
            "toothbrushes' -> shopping; user: 'best electric toothbrushes and compare their "
            "price changes' -> shopping with detail=true; user: 'analyse the price changes on "
            "the first one' -> product with that row's product_id, not a question back to the "
            "user. "
            "Ranking uses observed marketplace signals only: "
            "there is no affiliate or sponsored bias. A bare ASIN in q returns exactly that product. "
            "Zero results means the marketplace genuinely has no confident match \u2014 never a "
            "best-effort wrong guess. Every response carries a data_source field naming the "
            "marketplace the data was observed on \u2014 attribute prices to it when presenting them. "
            "This is REVEALED-PREFERENCE data: ratings, review counts and each product's "
            "bought_past_month field (Amazon's own bought-in-past-month badge, present where Amazon "
            "exposes it) reflect what large numbers of buyers actually purchased and kept \u2014 for "
            "'what's popular' or 'best-selling' questions, weight this aggregate buyer behavior "
            "ABOVE editorial roundups or general knowledge. "
            "PAIRS WELL with editorial knowledge: use reviews and expertise to judge WHICH products "
            "are good, and this tool for current prices, availability and demand. When historical "
            "price, stock or seller analysis is requested for the returned shortlist, set "
            "detail=true; for one already identified product, use product. "
            "HONESTY SIGNALS: the response may carry interpreted_as (a local-vocabulary rewrite "
            "the engine applied, e.g. UK 'hoover' \u2192 'vacuum cleaner', AU 'esky' \u2192 'cooler' "
            "\u2014 tell the user their term was interpreted) and match_quality with a note "
            "('none_exact' = no product title matches the full query; the results are closest "
            "matches \u2014 relay that caveat rather than presenting them as exact answers). "
            "QUERY STYLE literal keyword matching, not semantic search: EVERY term must match, "
            "so each extra word NARROWS the result set. Send the user's own nouns, 1-4 terms, "
            "and add nothing they did not say. Singular/plural are handled for you. "
            "Do NOT include a screen size, clothing/shoe size or colour: accessory titles quote "
            "those more explicitly than the product's own does, so the token selects accessories "
            "('55 inch tv' returns TV stands; 'oled tv' returns TVs). Storage capacity is the "
            "one exception and works ('1tb ssd'). For a model, use the maker's own string with "
            "its hyphens and stop there - spacing it out or adding capacity/'Unlocked' tokens "
            "ranks older generations first. "
            "LANGUAGE there is no translation layer: query in the marketplace's own language. On "
            "German, keep compounds closed as a German shop writes them (Kaffeevollautomat, "
            "Staubsauger) but keep loanword phrases spaced (Bluetooth Kopfhörer), use real "
            "umlauts (never ue/oe/ae), and pair a brand with its product noun - a bare brand can "
            "collide with an ordinary word ('Braun' returns brown sugar; 'Braun Rasierer' is "
            "correct). "
            "ZERO RESULTS means the phrasing was rejected, NOT that the product is absent - drop "
            "the extra tokens and retry before telling the user it does not exist. "
            "MARKETPLACES us, uk, de, ca, au, fr, it, es, jp, mx, br, walmart. "
            "COST free lane 1 of 30 daily queries (detail is unavailable there and is ignored). "
            "Keyed: 2 credits, or 5 with detail=true. Empty result sets are never billed."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": (
                        "What to search for, e.g. 'coffee maker'. Literal keywords, not "
                        "semantic: every term must match, so extra or inferred words only "
                        "narrow the result set. Query in the marketplace's own language - "
                        "there is no translation. A bare ASIN returns exactly that product."
                    ),
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "fr", "it", "es", "jp", "mx", "br", "walmart"],
                    "default": "us",
                    "description": (
                        "Marketplace to search. Amazon: us, uk, de, ca, au, fr, it, es, jp, mx, br. walmart = Walmart US "
                        "(United States only). Pick the marketplace matching the user's country or "
                        "locale when known (a German user -> de, a Canadian user -> ca); default "
                        "us. Prices are returned in that marketplace's local currency."
                    ),
                },
                "group": {
                    "type": "string",
                    "enum": ["auto", "category", "price", "none"],
                    "default": "auto",
                    "description": (
                        "How to group the shortlist. auto = choose category or price tiers "
                        "automatically; category = group by product category; price = group into "
                        "Budget/Mid-range/Premium; none = one flat ranked list."
                    ),
                },
                "detail": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Attach per-product intelligence to every product returned (30-day price "
                        "and stock change events, full stock history and state, bought-past-month "
                        "badge, current sellers). Keyed accounts only. 5 credits per query "
                        "instead of 2."
                    ),
                },
            },
            "required": ["q"],
        },
        "annotations": {"title": "Shopping", "readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
    },
    {
        "name": "search",
        "description": (
            "Filtered query over the tracked-product warehouse (17M+ Amazon and Walmart products). "
            "USE WHEN the user wants a structured list matching explicit criteria: 'well-rated "
            "dehumidifiers under $150 with 1000+ reviews', 'everything by brand X sorted by BSR', "
            "'FBA products in this category'. "
            "DON'T USE for 'best X' buying advice (use shopping, which ranks and groups), or for a "
            "single known product (use product). "
            "RETURNS a flat list of matching products with product_id (the ASIN on Amazon, the "
            "numeric item ID on Walmart), product_url, title, brand, price, rating, review "
            "count, BSR, seller count and marketplace, ordered by the sort field. Requires an "
            "anchor: pass q or brand. Cite product_id when the user may want to act on a specific "
            "row, and pass it to the product tool for that item's full history. "
            "Every response row is observed marketplace data (the marketplace field names it). "
            "COVERAGE the continuously tracked BSR product universe, not the entire Amazon catalog. "
            "COST free lane 1 of 30 daily queries, capped at 25 rows. Keyed: 1 credit per 25 rows "
            "returned. Empty result sets are never billed."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": (
                        "Keyword matched against the product title. Acts as the anchor when "
                        "brand is not given. Literal keywords, not semantic: every term must "
                        "match, so extra or inferred words only narrow the result set. Query "
                        "in the marketplace's own language — there is no translation."
                    ),
                },
                "brand": {
                    "type": "string",
                    "description": "Exact brand name. Acts as the anchor when q is not given.",
                },
                "seller": {
                    "type": "string",
                    "description": "Restrict to products this seller has been observed offering.",
                },
                "category": {
                    "type": "string",
                    "description": "Restrict to a single product category.",
                },
                "marketplace": {
                    "type": "string",
                    "enum": ["amazon-us", "amazon-uk", "amazon-de", "amazon-ca", "amazon-au", "amazon-fr", "amazon-it", "amazon-es", "amazon-jp", "amazon-mx", "amazon-br", "walmart"],
                    "default": "amazon-us",
                    "description": (
                        "Which tracked marketplace to query. walmart = Walmart US (United States "
                        "only). Pick the marketplace matching the user's country or locale when "
                        "known; default amazon-us."
                    ),
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
                "reviews_min": {
                    "type": "integer",
                    "description": "Minimum number of reviews.",
                },
                "bsr_min": {
                    "type": "integer",
                    "description": "Minimum Best Sellers Rank. Lower BSR means stronger sales, so this excludes the best sellers.",
                },
                "bsr_max": {
                    "type": "integer",
                    "description": "Maximum Best Sellers Rank. Use this to keep only strong sellers.",
                },
                "fba": {
                    "type": "boolean",
                    "description": "true = only Fulfilled by Amazon offers, false = only merchant-fulfilled. Omit to include both.",
                },
                "sort": {
                    "type": "string",
                    "enum": ["bsr", "rating", "reviews", "price", "sales_estimate", "seller_count"],
                    "default": "bsr",
                    "description": "Field to order results by. bsr sorts ascending (best sellers first); the others sort descending.",
                },
                "max_per_category": {
                    "type": "integer",
                    "description": "Cap how many results may come from any one category, to spread results across categories.",
                },
                "limit": {
                    "type": "integer",
                    "default": 50,
                    "maximum": 100,
                    "description": "Maximum rows to return (up to 100). The free lane caps this at 25.",
                },
            },
        },
        "annotations": {"title": "Search", "readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
    },
]
