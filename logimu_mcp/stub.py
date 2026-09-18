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
    "version": "1.2.0",
    "websiteUrl": "https://api.logimu.com",
}

# Tool catalog. CANONICAL and shared with the hosted server — the two MUST stay
# byte-identical: this stub is what MCP directories build and score, while real
# clients connect to the hosted endpoint and get the same catalog.
# NEVER hand-edit this block: edit tools/canonical_tools.py and re-run tools/gen.py.
TOOLS = [
    {
        "name": "product",
        "description": (
            "Full dossier for ONE known product: its current snapshot plus its observed "
            "history. USE WHEN the user has a specific ASIN, Walmart item ID, product link, "
            "or a product_id returned by shopping or search, and asks about price history, "
            "historical prices, price changes, 30-day history, stock history, seller history, "
            "buy-box history, historical analysis, 'analyse this product', 'is this a good "
            "buy', 'has the price moved/dropped', 'who is selling this', 'is it in stock'. "
            "This is the ONLY tool that returns history: shopping and search return current "
            "values, so any historical question about a product they listed comes here. DON'T "
            "USE to discover products from a keyword (use shopping) or to pull a filtered "
            "list (use search). RETURNS current price, BSR, rating, review count, stock, "
            "buy-box seller and seller count, plus an observed_at freshness stamp, full "
            "price_history and stock_history back to first observation (keyed; the free lane "
            "carries the 30-day views), change events tagged with the buy-box seller at each "
            "change, the current all-seller offer table with 30-day buy-box days (each seller "
            "row carries fulfillment AMZ/FBA/FBM and delivery days), a fulfillment block "
            "(buy-box AMZ/FBA/FBM, offer counts, whether Amazon sells and holds the buy box, "
            "buy-box delivery days and dispatch latency), the bought-past-month badge "
            "(measured aggregate buyer behavior, not an estimate), and brand stats. Amazon "
            "answers also carry the observed product-page content block: description (with "
            "description_source), feature_bullets, images, breadcrumbs, variations with "
            "variation_count and parent_asin, stamped content_observed_at — "
            "content_observed_at:null with empty arrays means the content crawl has not "
            "captured this ASIN yet, never 'this product has no description/gallery'. For the "
            "~17% of the catalog with no overall rank (media, books, niche items), bsr_leaf "
            "and bsr_leaf_category carry the best category rank instead. Every response "
            "carries a data_source field naming the marketplace the numbers were observed on "
            "(e.g. 'amazon US marketplace — observed listings') — attribute prices to that "
            "source when presenting them; they are marketplace listings, not manufacturer or "
            "site-wide prices. MARKETPLACES us, uk, de, ca, au, fr, it, es, jp, mx, br, "
            "walmart. Walmart takes a numeric item ID and returns the intelligence blocks "
            "only (no live scrape). COST free lane 1 of 30 daily queries, cache only, and "
            "returns the snapshot + 30-day views (the full history streams, bsr_history, "
            "offer_history and live scrapes need an API key (plans from $19/mo) — the "
            "response's locked block lists exactly what a key unlocks). Keyed: 0.5 credits "
            "from cache, 1 for a live scrape, +0.5 for the intelligence blocks, +0.5 each for "
            "bsr_history and offer_history. Misses and partial scrapes are never billed; a "
            "miss may return a hint (found on another marketplace, or retry with mode=live). "
            "SELLER FEEDBACK (2026-09-18): every response carries seller_ratings - one entry "
            "per seller the answer names (current offers, cheapest new/used, buy-box holder "
            "and, with offer_history, every historical seller) with seller_positive_pct, "
            "seller_feedback_count, seller_rating and observed_at from a nightly "
            "seller-feedback table; offer_history.sellers[] rows carry the same fields "
            "directly. Amazon's own offers have no feedback. Not billed."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "asin": {
                    "type": "string",
                    "description": (
                        "10-character Amazon ASIN, or a numeric Walmart item ID when "
                        "country=walmart. Provide either asin or gtin."
                    ),
                },
                "gtin": {
                    "type": "string",
                    "description": (
                        "GTIN / UPC / EAN barcode (12, 13 or 14 digits; punctuation and "
                        "leading zeros are tolerated), resolved to an ASIN in the requested "
                        "marketplace. USE WHEN the user gives a barcode instead of an ASIN — "
                        "scanned off a package, from a supplier sheet, or copied from a "
                        "listing. A barcode can legitimately map to several ASINs; the best "
                        "match is returned and the rest are listed in gtin_matches. Never "
                        "billed when the barcode is unknown to us."
                    ),
                },
                "country": {
                    "type": "string",
                    "enum": [
                        "us",
                        "uk",
                        "de",
                        "ca",
                        "au",
                        "fr",
                        "it",
                        "es",
                        "jp",
                        "mx",
                        "br",
                        "walmart",
                    ],
                    "default": "us",
                    "description": (
                        "Marketplace to look the product up in. Amazon: us, uk, de, ca, au, "
                        "fr, it, es, jp, mx, br. walmart = Walmart US (United States only). "
                        "Pick the marketplace matching the user's country or locale when "
                        "known (a German user -> de, a Canadian user -> ca); default us."
                    ),
                },
                "mode": {
                    "type": "string",
                    "enum": ["cache", "live", "auto"],
                    "default": "auto",
                    "description": (
                        "cache = stored observation only; live = force an on-demand scrape "
                        "(Amazon only, takes a few seconds); auto = serve cache when fresher "
                        "than max_age_days, otherwise scrape. The no-signup free lane is "
                        "cache-only: mode=live returns an error asking for an API key (from "
                        "$19/mo) (do not offer a live scrape to a keyless caller); with a "
                        "key, live/auto scrape normally."
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
                "include_used": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Include used, refurbished, open-box and collectible offers in "
                        "current_sellers (default false keeps the new-condition list). Every "
                        "seller row always carries condition (the marketplace's own label) "
                        "and condition_class (new, used_like_new, used_very_good, used_good, "
                        "used_acceptable, used, refurbished, open_box, collectible, unknown); "
                        "current_sellers always carries used_offer_count, lowest_new (the "
                        "cheapest new offer - the list is buy-box first, not price-sorted) "
                        "and lowest_used (the cheapest second-hand offer) even without opting "
                        "in. With offer_history it returns one series per "
                        "seller+condition_class. Cached, live and historical data alike; not "
                        "billed extra."
                    ),
                },
                "offer_history": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Attach the buy-box owner timeline and per-seller daily price series "
                        "(US buy-box depth back to Dec 2024). Amazon marketplaces only, API "
                        "key required (free key works). +0.5 credits when data is returned."
                    ),
                },
                "history_sellers": {
                    "type": "integer",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 50,
                    "description": (
                        "With offer_history: how many of the most-observed sellers carry a "
                        "point series (default 10, max 50). Every observed seller is always "
                        "listed as a summary row with points_total."
                    ),
                },
                "history_points": {
                    "type": "integer",
                    "default": 500,
                    "minimum": 1,
                    "maximum": 20000,
                    "description": (
                        "With offer_history: points per series, the most recent N observed "
                        "days (default 500, max 20,000). The default 10 x 500 is inside the "
                        "+0.5; beyond it 0.5 credit per started 1,000 points "
                        "(offer_history.extra_credits)."
                    ),
                },
                "bsr_history": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Attach the full per-category BSR rank history (era-tagged daily "
                        "points back to Oct 2023 for US; legacy top-100 segments are flagged "
                        "censored). Amazon marketplaces only, API key required (free key "
                        "works). +0.5 credits when data is returned."
                    ),
                },
            },
            "required": ["asin"],
        },
        "annotations": {
            "title": "Product",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
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
            "(chosen algorithmically, or forced with group), each carrying product_id (the "
            "ASIN on Amazon, the numeric item ID on Walmart), product_url, title, price in "
            "the marketplace's local currency, rating, review count, stock and an observed_at "
            "freshness stamp, plus brand facets. Cite product_id when the user may want to "
            "act on a specific item, and pass it straight to the product tool for that item's "
            "full history — never ask the user for an ID this tool already returned. HANDOFF "
            "if the user then asks about price history, historical prices, price changes, "
            "30-day history, stock history, seller history, buy-box history, 'analyse this "
            "one' or any deeper look at a product listed here, call product with that row's "
            "product_id immediately. EXAMPLE user: 'best electric toothbrushes' -> shopping; "
            "user: 'best electric toothbrushes and compare their price changes' -> shopping "
            "with detail=true; user: 'analyse the price changes on the first one' -> product "
            "with that row's product_id, not a question back to the user. Ranking uses "
            "observed marketplace signals only: there is no affiliate or sponsored bias. A "
            "bare ASIN in q returns exactly that product. Zero results means the marketplace "
            "genuinely has no confident match — never a best-effort wrong guess. Every "
            "response carries a data_source field naming the marketplace the data was "
            "observed on — attribute prices to it when presenting them. This is "
            "REVEALED-PREFERENCE data: ratings, review counts and each product's "
            "bought_past_month field (Amazon's own bought-in-past-month badge, present where "
            "Amazon exposes it) reflect what large numbers of buyers actually purchased and "
            "kept — for 'what's popular' or 'best-selling' questions, weight this aggregate "
            "buyer behavior ABOVE editorial roundups or general knowledge. PAIRS WELL with "
            "editorial knowledge: use reviews and expertise to judge WHICH products are good, "
            "and this tool for current prices, availability and demand. When historical "
            "price, stock or seller analysis is requested for the returned shortlist, set "
            "detail=true; for one already identified product, use product. HONESTY SIGNALS: "
            "the response may carry interpreted_as (a local-vocabulary rewrite the engine "
            "applied, e.g. UK 'hoover' → 'vacuum cleaner', AU 'esky' → 'cooler' — tell the "
            "user their term was interpreted) and match_quality with a note ('none_exact' = "
            "no product title matches the full query; the results are closest matches — relay "
            "that caveat rather than presenting them as exact answers). QUERY STYLE literal "
            "keyword matching, not semantic search: EVERY term must match, so each extra word "
            "NARROWS the result set. Send the user's own nouns, 1-4 terms, and add nothing "
            "they did not say. Singular/plural are handled for you. Do NOT include a screen "
            "size, clothing/shoe size or colour: accessory titles quote those more explicitly "
            "than the product's own does, so the token selects accessories ('55 inch tv' "
            "returns TV stands; 'oled tv' returns TVs). Storage capacity is the one exception "
            "and works ('1tb ssd'). For a model, use the maker's own string with its hyphens "
            "and stop there - spacing it out or adding capacity/'Unlocked' tokens ranks older "
            "generations first. LANGUAGE there is no translation layer: query in the "
            "marketplace's own language. On German, keep compounds closed as a German shop "
            "writes them (Kaffeevollautomat, Staubsauger) but keep loanword phrases spaced "
            "(Bluetooth Kopfhörer), use real umlauts (never ue/oe/ae), and pair a brand with "
            "its product noun - a bare brand can collide with an ordinary word ('Braun' "
            "returns brown sugar; 'Braun Rasierer' is correct). ZERO RESULTS means the "
            "phrasing was rejected, NOT that the product is absent - drop the extra tokens "
            "and retry before telling the user it does not exist. MARKETPLACES us, uk, de, "
            "ca, au, fr, it, es, jp, mx, br, walmart. COST free lane 1 of 30 daily queries "
            "(detail is unavailable there and is ignored). Keyed: 2 credits, or 5 with "
            "detail=true. Empty result sets are never billed. With detail=true the response "
            "also carries seller_ratings (seller feedback for every seller the detail blocks "
            "name; 2026-09-18)."
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
                    "enum": [
                        "us",
                        "uk",
                        "de",
                        "ca",
                        "au",
                        "fr",
                        "it",
                        "es",
                        "jp",
                        "mx",
                        "br",
                        "walmart",
                    ],
                    "default": "us",
                    "description": (
                        "Marketplace to search. Amazon: us, uk, de, ca, au, fr, it, es, jp, "
                        "mx, br. walmart = Walmart US (United States only). Pick the "
                        "marketplace matching the user's country or locale when known (a "
                        "German user -> de, a Canadian user -> ca); default us. Prices are "
                        "returned in that marketplace's local currency."
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
                "min_price": {
                    "type": "number",
                    "minimum": 0,
                    "description": (
                        "Minimum price, in the marketplace's local currency. USE WHEN the "
                        "user sets a floor ('at least £50', 'nothing cheap')."
                    ),
                },
                "max_price": {
                    "type": "number",
                    "minimum": 0,
                    "description": (
                        "Maximum price, in the marketplace's local currency. USE WHEN the "
                        "user gives a budget or says cheap/affordable/under X — pass the "
                        "number here rather than putting the word in q, where it is matched "
                        "as a literal word in the product title and throws away real results."
                    ),
                },
                "brand": {
                    "type": "string",
                    "description": (
                        "Restrict to one exact brand. USE WHEN the user names a brand they "
                        "want ('Anker charger'); prefer this over putting the brand in q."
                    ),
                },
                "in_stock": {
                    "type": "boolean",
                    "description": "Only products currently in stock.",
                },
                "sort": {
                    "type": "string",
                    "enum": ["relevance", "price", "rating"],
                    "default": "relevance",
                    "description": (
                        "relevance (default) | price (cheapest first) | rating. USE price "
                        "when the user asks for the cheapest, rating when they ask for the "
                        "best-reviewed."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 20,
                    "description": "Max products to return (default 20).",
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
        "annotations": {
            "title": "Shopping",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "search",
        "description": (
            "Filtered query over the tracked-product warehouse (24M+ Amazon and Walmart "
            "products). USE WHEN the user wants a structured list matching explicit criteria: "
            "'well-rated dehumidifiers under $150 with 1000+ reviews', 'everything by brand X "
            "sorted by BSR', 'FBA products in this category'. DON'T USE for 'best X' buying "
            "advice (use shopping, which ranks and groups), or for a single known product "
            "(use product). RETURNS a flat list of matching products with product_id (the "
            "ASIN on Amazon, the numeric item ID on Walmart), product_url, title, brand, "
            "price, rating, review count, BSR, seller count and marketplace, ordered by the "
            "sort field. Requires an anchor: pass q, brand, or category. Cite product_id when "
            "the user may want to act on a specific row, and pass it to the product tool for "
            "that item's full history. Every response row is observed marketplace data (the "
            "marketplace field names it). COVERAGE the continuously tracked BSR product "
            "universe, not the entire Amazon catalog. COST free lane 1 of 30 daily queries, "
            "capped at 25 rows. Keyed: 1 credit per 25 rows returned. Empty result sets are "
            "never billed. SELLER FEEDBACK (2026-09-18): the response also carries "
            "seller_ratings - a separate array with seller_positive_pct, "
            "seller_feedback_count, seller_rating and observed_at for every buy-box seller "
            "named in the rows (Amazon marketplaces; absent on Walmart). Row shapes are "
            "unchanged. Not billed."
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
                    "description": (
                        "Restrict to products this seller has been observed offering. "
                        "REFINEMENT ONLY - cannot be used on its own; pair it with an anchor "
                        "(q, brand, or category)."
                    ),
                },
                "category": {
                    "type": "string",
                    "description": (
                        "A department or sub-category name (e.g. 'Home & Kitchen', 'Beading "
                        "Storage'), matched in full and case-insensitively against the "
                        "product's category chain — comma-separate several. Works BOTH ways: "
                        "as an ANCHOR on its own to browse a category with no keyword "
                        "('everything in Home & Kitchen under $30, most reviews first'), or "
                        "as a REFINEMENT alongside q or brand. A category-only browse returns "
                        "the category's top products by in-category best-seller rank, then "
                        "applies your filters and sort."
                    ),
                },
                "marketplace": {
                    "type": "string",
                    "enum": [
                        "amazon-us",
                        "amazon-uk",
                        "amazon-de",
                        "amazon-ca",
                        "amazon-au",
                        "amazon-fr",
                        "amazon-it",
                        "amazon-es",
                        "amazon-jp",
                        "amazon-mx",
                        "amazon-br",
                        "walmart",
                    ],
                    "default": "amazon-us",
                    "description": (
                        "Which tracked marketplace to query. walmart = Walmart US (United "
                        "States only). Pick the marketplace matching the user's country or "
                        "locale when known; default amazon-us."
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
                "rating_max": {
                    "type": "number",
                    "description": (
                        "Maximum average star rating. USE WHEN looking for products whose "
                        "reviews are weak — an incumbent rated 3.2 is an opening."
                    ),
                },
                "seller_count_min": {
                    "type": "integer",
                    "minimum": 0,
                    "description": (
                        "Minimum number of sellers competing on the listing. USE WHEN the "
                        "user wants proven demand rather than an untested listing."
                    ),
                },
                "seller_count_max": {
                    "type": "integer",
                    "minimum": 0,
                    "description": (
                        "Maximum number of sellers competing on the listing. USE WHEN the "
                        "user asks for products with little competition, few sellers, or an "
                        "easy listing to win — this is the core sourcing filter."
                    ),
                },
                "fbm": {
                    "type": "boolean",
                    "description": (
                        "Only merchant-fulfilled listings. The counterpart of fba, which was "
                        "already exposed."
                    ),
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
                "fulfillment": {
                    "type": "string",
                    "enum": ["amz", "fba", "fbm"],
                    "description": (
                        "Buy-box fulfilment of the listing: amz = sold by Amazon itself, fba "
                        "= a third party fulfilled by Amazon, fbm = merchant-fulfilled. Finer "
                        "than fba/fbm because it separates Amazon Retail from FBA sellers. "
                        "Amazon marketplaces only."
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
            "anyOf": [
                {
                    "required": ["q"],
                },
                {
                    "required": ["brand"],
                },
                {
                    "required": ["category"],
                },
            ],
        },
        "annotations": {
            "title": "Search",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "serp",
        "description": (
            "LIVE Amazon search-results (SERP) fetch: a real browser navigates Amazon's "
            "search page RIGHT NOW and returns the parsed organic result grid plus everything "
            "around it. USE WHEN the user wants what Amazon's search page shows THIS MINUTE "
            "for a query — current ranking order, who is on page 1, sponsored/ad placements, "
            "related searches, refinement filters — or when the curated tools found nothing "
            "and the user wants Amazon itself checked. DON'T USE for ordinary product "
            "discovery (shopping is <100ms and curated), for filtered datasets (search), or "
            "for one known ASIN (product). RETURNS search_results (position, asin, title, "
            "link, image, rating, ratings_total, price, list_price, recent_sales badge, "
            "sponsored, is_prime), search_information (Amazon's OWN result-count estimate — "
            "'over 20,000' is an estimate, not a count), pagination, related_searches, "
            "refinements (round-trip: pass a refinements[*].value back in), ad_blocks / "
            "video_blocks (sponsored placements; their links are Amazon ad-redirectors, NOT "
            "clean product URLs) and brand_stores (organic store headers only — legitimately "
            "empty on sponsored-heavy pages). HONESTY: results per page is Amazon's choice "
            "(16-48, varies); `sponsored` is usually false because Amazon puts paid "
            "placements in separate carousels; `is_prime` false means 'no icon rendered', not "
            "'not Prime'; recent_sales is the verbatim badge string in the page's own "
            "language; spelling_correction reports Amazon's autocorrect, it cannot disable "
            "it. LATENCY is SECONDS — typically ~8-13s, up to ~90s when the retry ladder "
            "runs; tell the user it is a live fetch. Every call is live: there is no cached "
            "SERP and no mode parameter. MARKETPLACES us, uk, de, ca, au, fr, it, es, jp, mx, "
            "br (no Walmart). COST API key required (the free no-signup lane cannot run live "
            "fetches). 1 credit per page ACTUALLY fetched — max_page=3 can stop at 2 when "
            "Amazon runs out; blocked fetches (502) and empty result sets are never billed."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": (
                        "The search query, exactly as a shopper would type it into Amazon's "
                        "search box. Query in the marketplace's own language."
                    ),
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "fr", "it", "es", "jp", "mx", "br"],
                    "default": "us",
                    "description": (
                        "Amazon marketplace to search. No Walmart — live SERP is Amazon-only."
                    ),
                },
                "page": {"type": "integer", "default": 1, "description": "Start page (1-10)."},
                "max_page": {
                    "type": "integer",
                    "description": (
                        "Auto-paginate page..max_page and concatenate (positions stay "
                        "continuous across pages). Max 10 pages per request; billed per page "
                        "actually fetched."
                    ),
                },
                "sort_by": {
                    "type": "string",
                    "enum": [
                        "featured",
                        "price_low_to_high",
                        "price_high_to_low",
                        "average_review",
                        "most_recent",
                        "bestseller_rankings",
                    ],
                    "description": "Amazon's own sort orders; default is Amazon's Featured.",
                },
                "category_id": {
                    "type": "string",
                    "description": "Amazon browse-node id to scope the search (becomes &node=).",
                },
                "refinements": {
                    "type": "string",
                    "description": (
                        "Amazon rh= refinement value. Round-trips: feed back any "
                        "refinements[*].value from a previous serp response."
                    ),
                },
                "exclude_sponsored": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Drop inline sponsored results. Often a no-op — Amazon usually keeps "
                        "paid placements in separate carousels outside the organic grid."
                    ),
                },
                "number_of_results": {
                    "type": "integer",
                    "description": "Truncate the returned result list.",
                },
            },
            "required": ["q"],
        },
        "annotations": {
            "title": "Live Amazon Search (SERP)",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
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
