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
    "version": "1.7.0",
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
            "(measured aggregate buyer behavior, not an estimate), brand stats, and since "
            "2026-09-27: dimensions (item weight + package size as printed plus parsed metric "
            "weight_g / *_cm), deal_history (list price, savings and coupon/promotion text as "
            "segments of consecutive observations, with a current view), "
            "bought_past_month_history (the badge over time; null = page seen without a "
            "badge), rating_history (rating_count + rating per observed day with "
            "ratings_gained_30d/90d), and variation_coverage (the variation matrix as last "
            "seen with, per child, whether we track it and its latest 30-day price - current "
            "state, not history). With offer_history=true every per-seller point also carries "
            "that day's shipping cost, fba and prime, and the answer carries "
            "buybox_price_history (2026-10-09): the lowest buy-box price of every observed "
            "day, oldest first, each point labelled source offers (our offer observations, "
            "every Amazon marketplace, from 2026-04-17) or daily_snapshot (the legacy daily "
            "snapshot, Amazon US back to Nov 2023) - the deepest price series we hold; a gap "
            "between two dates is a stretch we did not observe. Since 2026-10-14 every Amazon "
            "answer also carries buybox_price_points_hot: every all-offers-page observation "
            "of the last 30 days, newest last, {ts, price, seller, seller_id, fulfillment, "
            "offer_count} - sub-daily for ASINs in our hot lane, which refreshes popular and "
            "customer-polled ASINs every few hours (null when none; history_only carries it "
            "too) - and tracking: the lane's state for the ASIN (hot, interval_min, "
            "last_fetched_at) or null. Since 2026-10-15 Amazon answers carry buybox_condition "
            "(new | used | null = no featured offer; with buybox_condition_source "
            "product_page | offers_page and buybox_condition_detail: the pinned offer's "
            "condition text, used_only_buybox, or the used storefront's name - Amazon Resale "
            "/ Amazon Warehouse win the buy box like any seller and read as Amazon retail "
            "before), buybox_state (what the lane's newest all-offers read saw: in_stock | "
            "no_buybox | out_of_stock, with buybox_state_observed_at and stock_state_source "
            "when it decided stock_state; stock_state, in_stock and out_of_stock always "
            "agree), and on LIVE answers variation_status (page_is_sibling | page_is_other | "
            "null) + page_asin when Amazon served another ASIN's page for the one asked "
            "(cache answers: null). Amazon answers also carry the observed product-page "
            "content, the byline (authors[] with role_norm "
            "author/narrator/illustrator/editor/translator + author for books, audiobooks, "
            "music; 2026-09-29), the book/media format (format, format_norm, and formats[]: "
            "every format of the book, each its own ASIN with price and membership "
            "subscription_price, plus family_asin; 2026-09-30) block: description (with "
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
            "walmart. Walmart takes a numeric item ID (or gtin= with the item's UPC) and "
            "returns the intelligence blocks plus its listing content: image_url, "
            "description, breadcrumbs, highlights (spec name/value pairs), warnings, upc, "
            "rating/review_count, was_price, in_stock, and shipping_cost per seller; "
            "mode=live reads the walmart.com page now (2 credits, typically 8-15 s, one page: "
            "the cheapest other seller is not fetched; location names the store it was priced "
            "for) and mode=auto serves our record when observed within max_age_days, else "
            "reads live. COST free lane 1 of 30 daily queries, cache only, and returns the "
            "snapshot + 30-day views (the full history streams, bsr_history, offer_history "
            "and live scrapes need an API key (plans from $19/mo) — the response's locked "
            "block lists exactly what a key unlocks). Keyed: 0.5 credits from cache with "
            "everything included - bsr_history and offer_history too, no extra charge since "
            "2026-10-10 - and 1 for a live scrape (2 on Walmart); history_only=true returns "
            "just the history series for 0.05 credit. Misses and partial scrapes are never "
            "billed; a miss may return a hint (found on another marketplace, or retry with "
            "mode=live). SELLER FEEDBACK (2026-09-18): every response carries seller_ratings "
            "- one entry per seller the answer names (current offers, cheapest new/used, "
            "buy-box holder and, with offer_history, every historical seller) with "
            "seller_positive_pct, seller_feedback_count, seller_rating and observed_at from a "
            "nightly seller-feedback table; offer_history.sellers[] rows carry the same "
            "fields directly. Amazon's own offers have no feedback. Not billed."
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
                        "(US buy-box depth back to Dec 2024) plus buybox_price_history, the "
                        "lowest buy-box price of every observed day (Amazon US back to Nov "
                        "2023). Amazon marketplaces only; needs a paid-plan API key (from "
                        "$19/mo). Included in the record, no extra credits."
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
                        "days (default 500, max 20,000). Wider series are included too, no "
                        "extra credits (offer_history.points_extra still reports the points "
                        "beyond the default 10 x 500)."
                    ),
                },
                "bsr_history": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Attach the full per-category BSR rank history (era-tagged daily "
                        "points back to Oct 2023 for US; legacy top-100 segments are flagged "
                        "censored). Amazon marketplaces only; needs a paid-plan API key (from "
                        "$19/mo). Included in the record, no extra credits."
                    ),
                },
                "history_only": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Return ONLY the stored history series - bsr_history, offer_history "
                        "and buybox_price_history - with no snapshot, content or seller "
                        "table, for 0.05 credit. USE WHEN the user tracks price or rank over "
                        "time for many products and does not need the current listing. Amazon "
                        "marketplaces only, served from stored observations (mode=live is "
                        "refused); needs a paid-plan API key (from $19/mo)."
                    ),
                },
                "track": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Answer AND track (paid plans): after this answer the ASIN is pinned "
                        "into our hot lane, which re-reads its all-offers page every "
                        "`interval` for 30 days and adds every read to "
                        "buybox_price_points_hot - the same as the track_product tool. No "
                        "extra credits (the plan's daily tracked-snapshot allowance is "
                        "drawn); the answer is served even when the tracking is refused and "
                        "its `track` block says why. Amazon only."
                    ),
                },
                "interval": {
                    "type": "string",
                    "enum": ["1h", "2h", "4h", "12h", "24h"],
                    "default": "4h",
                    "description": (
                        "With track=true: how often the lane re-reads the all-offers page (1h "
                        "= 24 snapshots a day)."
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
            "detail=true. Empty result sets are never billed. detail=true attaches to EVERY "
            "product everything the basic product call carries (2026-09-28): current sellers "
            "with fulfillment and delivery, 30-day price/stock events, stock history, "
            "brand_stats, dimensions, deal/badge/rating history, variation coverage, page "
            "content and up to 50 featured reviews, plus a response-wide seller_ratings "
            "array; only bsr_history and offer_history stay product-only."
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
                "format": {
                    "type": "string",
                    "description": (
                        "Books/media only: return only this format - kindle, paperback, "
                        "hardcover, mass_market, audiobook, audio_cd, board_book, spiral, "
                        "library_binding or other (comma-separate several). USE WHEN the user "
                        "wants a specific edition ('LOTR in paperback', 'the audiobook')."
                    ),
                },
                "collapse": {
                    "type": "boolean",
                    "default": True,
                    "description": (
                        "true (default): one row per book, its other formats listed in the "
                        "row's `formats` (each with its own ASIN and price). false: every "
                        "format as its own row."
                    ),
                },
                "include_unavailable": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "false (default): only products with a current offer, so the "
                        "shortlist is buyable. true: also list items that currently have NO "
                        "offer on the marketplace (Amazon 'Currently unavailable': price "
                        "null, in_stock false). USE WHEN the user asks about a specific "
                        "discontinued or sold-out product; otherwise leave it off."
                    ),
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
        "name": "seller",
        "description": (
            "Amazon SELLER profile by seller id, optionally with the products the seller "
            "sells. USE WHEN the user asks about a third-party seller / merchant / storefront "
            "(who they are, how they are rated, what they sell) - the seller id is the 'A...' "
            "code in /sp?seller=... or the seller_id on any offer the product tool returns. "
            "RETURNS seller (name, rating, lifetime and 12-month rating counts, positive %, "
            "is_amazon), feedback_summary per period (30 d / 90 d / 12 m / lifetime: average "
            "rating + count - Amazon no longer publishes positive/neutral/negative splits), "
            "rating_histogram, recent_feedback (up to 5 entries as date / rating / struck "
            "ONLY - never the buyer's name or text), and business (legal name, registration / "
            "VAT numbers, address, phone, email, representative) where the seller publishes "
            "it on Amazon - all 11 marketplaces; au and ca pages carry no business block, so "
            "it is null there. With products=true, also seller_products: mode=live the "
            "storefront as Amazon shows it now (the serp object, SECONDS), mode=cache the "
            "products we OBSERVED the seller offering (25 per page, buy-box days, observed "
            "price range, <100 ms). MODES for the profile: cache = our stored observation - "
            "the seller page as our tracker last read it (the full profile; sellers are "
            "re-read about every 14 days), or the page fetched in the last 24 h, or for "
            "sellers not stored yet the warehouse rating record; live = fetch the seller page "
            "now (5-20 s, up to ~30 s); auto (default) = stored when younger than "
            "max_age_days (default 14), else live. tracking{} says since when we have "
            "observed the seller (observed_first_seen), when last (last_observed) and how "
            "often - OBSERVED, never 'founded' or 'active since'. With history=true also "
            "history{}: the seller's rating change points (positive %, star rating, counts "
            "per 30 d / 90 d / 12 m / lifetime) and storefront-size points, oldest first, UTC "
            "- change points, each value holds until the next; the series starts 2026-10-04 "
            "at the earliest, so expect 1-2 points per seller for now. HONESTY: a 404 means "
            "Amazon has no seller page for that id on that marketplace (or we never observed "
            "it, in cache mode); a 502 is a collection failure, not a fact about the seller - "
            "retry. An empty storefront does not confirm the seller exists. LOOKUP: give "
            "seller_id, or name (resolved through observed buy-box data to the id, free). "
            "COST: paid plan required - the tool is listed only for keys on a paid plan (no "
            "free lane). Profile: 1 credit live, 0.5 from cache, auto bills what was served; "
            "history=true +0.5 once when at least one point comes back. Products: 1 credit "
            "per storefront page fetched (live) or per page of 25 observed products (cache). "
            "Feedback, business details and tracking are included at no extra charge. Not "
            "found, unavailable, blocked, empty storefront, empty history: 0. DERIVED "
            "(2026-10-05): brands=true adds the operator footprint - the brands this seller "
            "was observed winning the buy box on, with buy-box days (+1 credit per page of "
            "25); network=true adds the connected sellers that win on the same brands (+1 "
            "credit)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "seller_id": {
                    "type": "string",
                    "description": "Amazon seller id: 'A' + 8-24 letters/digits.",
                },
                "name": {
                    "type": "string",
                    "description": (
                        "Instead of seller_id: the seller's display name as Amazon prints it "
                        "(e.g. 'Total Office Solutions'). Resolved through observed buy-box "
                        "data to the seller id; a name we have never observed, or one with no "
                        "id on record, returns guidance - nothing is billed."
                    ),
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "fr", "it", "es", "jp", "mx", "br"],
                    "default": "us",
                    "description": (
                        "Amazon marketplace. No Walmart - seller pages are Amazon-only."
                    ),
                },
                "mode": {
                    "type": "string",
                    "enum": ["cache", "live", "auto"],
                    "default": "auto",
                    "description": (
                        "Profile lane (see description). products=true uses products_mode."
                    ),
                },
                "max_age_days": {
                    "type": "integer",
                    "default": 14,
                    "description": (
                        "auto only: how old the stored observation may be before fetching "
                        "live (default 14 = the tracker's cadence)."
                    ),
                },
                "history": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Also return history{} (rating + storefront-size change points, "
                        "oldest first, UTC). +0.5 credit when non-empty."
                    ),
                },
                "history_points": {
                    "type": "integer",
                    "default": 500,
                    "description": (
                        "history=true: the latest N change points per series (1-5000)."
                    ),
                },
                "products": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Also return the seller's products (billed separately, see "
                        "description)."
                    ),
                },
                "products_mode": {
                    "type": "string",
                    "enum": ["cache", "live"],
                    "default": "cache",
                    "description": (
                        "cache = observed products (fast); live = the storefront now "
                        "(seconds)."
                    ),
                },
                "page": {
                    "type": "integer",
                    "default": 1,
                    "description": (
                        "Products page (cache: 25 per page; live: Amazon's page 1-10)."
                    ),
                },
                "max_page": {
                    "type": "integer",
                    "description": (
                        "live products only: auto-paginate up to this page (max 10); billed "
                        "per page fetched."
                    ),
                },
                "brands": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Also return the operator footprint: brands this seller was observed "
                        "winning the buy box on (16 months), 25 per page (brands_page). +1 "
                        "credit per page."
                    ),
                },
                "brands_page": {"type": "integer", "default": 1},
                "network": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Also return connected sellers: sellers winning the buy box on the "
                        "same brands, strongest overlap first (max 50). +1 credit."
                    ),
                },
            },
            "anyOf": [
                {
                    "required": ["seller_id"],
                },
                {
                    "required": ["name"],
                },
            ],
        },
        "annotations": {
            "title": "Seller profile",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
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
            "br, walmart (live walmart.com search: 2 credits per results page, at most 3 "
            "pages a call, location names the store it was priced for; category_id and "
            "refinements are Amazon-only). COST API key required (the free no-signup lane "
            "cannot run live fetches). 1 credit per page ACTUALLY fetched — max_page=3 can "
            "stop at 2 when Amazon runs out; blocked fetches (502) and empty result sets are "
            "never billed."
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
                        "Amazon marketplace to search, or walmart (a live walmart.com "
                        "search)."
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
    {
        "name": "bestsellers",
        "description": (
            "LIVE Amazon Best Sellers list for one category: up to 100 products in Amazon's "
            "rank order, the category's full breadcrumb name, and its subcategories with "
            "their URLs. Given a marketplace's root best-sellers URL (or just a country) it "
            "returns the top-level categories instead, so you can walk the tree: root -> "
            "category -> subcategory, always by the URLs a previous answer returned. USE WHEN "
            "the user asks what sells best in a category or department right now, wants a "
            "top-100 or best-seller list, or wants to browse Amazon's best-seller categories. "
            "DON'T USE for a keyword search (serp is Amazon's live results page, shopping a "
            "curated shortlist), for one known ASIN (product), or for a product's rank "
            "history (product with bsr_history). RETURNS page_type 'category': "
            "current_category (name, full_name = the breadcrumb path, path[] with each "
            "ancestor's name/url/node_id, node_id, url), subcategories[] (name, url, "
            "node_id), bestsellers[] (rank, asin, title, link, image, rating, ratings_total, "
            "price) and pagination; page_type 'root': categories[] (name, url, node_id). "
            "Every answer carries observed_at (when the list was fetched from Amazon) and "
            "cached. HONESTY: names are in the page's language (German pages are local; fr, "
            "it, es, jp, mx and br pages are requested in English); ranks are Amazon's at "
            "fetch time; price is null when the card shows none; node_id is null for "
            "departments whose URL carries only a slug. LATENCY is SECONDS: ~15-35s for a "
            "fresh top 100, ~15s for a root list; Amazon refreshes these lists hourly, so an "
            "answer may come from our cache (up to 30 min for a category, 24 h for the root "
            "list) and then returns in milliseconds. MARKETPLACES us, uk, de, ca, au, fr, it, "
            "es, jp, mx, br (the marketplace comes from the URL; no Walmart). COST API key "
            "required (the free no-signup lane cannot run live fetches). 1 credit per page of "
            "50 products returned (the full top 100 = 2), cached or fresh; the root list is "
            "free; a category Amazon does not have, a blocked fetch and an empty list are "
            "never billed."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": (
                        "An Amazon Best Sellers URL: a category (e.g. "
                        "https://www.amazon.com/gp/bestsellers/kitchen/289814, or any URL "
                        "from a previous answer's subcategories / categories / path) or a "
                        "marketplace's root (https://www.amazon.de/gp/bestsellers/). The "
                        "marketplace comes from the host."
                    ),
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "fr", "it", "es", "jp", "mx", "br"],
                    "description": (
                        "Without url: that marketplace's root list of top-level categories "
                        "(start here when you have no URL yet). With url: must match the "
                        "URL's marketplace."
                    ),
                },
                "pages": {
                    "type": "integer",
                    "default": 2,
                    "minimum": 1,
                    "maximum": 2,
                    "description": (
                        "1 = ranks 1-50 (1 credit), 2 = ranks 1-100 (default, 2 credits). "
                        "Ignored for the root list."
                    ),
                },
            },
            "anyOf": [
                {
                    "required": ["url"],
                },
                {
                    "required": ["country"],
                },
            ],
        },
        "annotations": {
            "title": "Amazon Best Sellers (live)",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    },
    {
        "name": "offers",
        "description": (
            "LIVE Amazon offers page for one product: every seller offering it right now, "
            "read from Amazon's 'All offers' view at request time, every page of it (up to "
            "10). Each offer has the seller and seller_id, price, shipping_cost, condition, "
            "buy box, FBA / FBM / Amazon, Prime, ships-from, the delivery promise and the "
            "seller's feedback record; the answer adds the buy box and the page's own header "
            "(title, image, rating, review count). No product page is fetched. USE WHEN the "
            "user asks who sells a product right now, wants every current offer, the cheapest "
            "new or used offer or the buy-box winner as of this minute, or needs a fresh "
            "seller list before buying, sourcing or repricing. DON'T USE for brand, BSR, "
            "listing content, reviews or price / offer history (product), for a keyword "
            "search (shopping, serp) or for a brand's or a seller's long-run buy-box record "
            "(brand, seller). RETURNS asin, marketplace, observed_at, title, image_url, "
            "rating, reviews_count, currency, price (the buy box), buybox_seller, "
            "buybox_seller_id, seller_count, no_sellers, pages_fetched, buybox_condition / "
            "buybox_condition_source / buybox_condition_detail (new | used | null = no "
            "featured offer; the pinned offer's condition text or the used storefront's name, "
            "e.g. Amazon Resale), current_sellers (sellers[] buy box first, then price "
            "ascending: seller, seller_id, price, shipping_cost, condition, condition_class, "
            "is_buybox, is_fba, is_prime, fulfillment, ships_from, delivery, seller_rating, "
            "plus buybox_days_30d and the 30-day buy-box shares from our observations; "
            "offer_count, used_offer_count, lowest_new, lowest_used), fulfillment (offer "
            "counts by AMZ / FBA / FBM, whether Amazon sells or holds the buy box) and "
            "seller_ratings; with gtin also gtin_resolution (source, confidence, "
            "barcode_verified). HONESTY: no_sellers=true means Amazon lists no offer for the "
            "product right now, an answer confirmed by a second, independent fetch before it "
            "is served; a fetch that fails is reported as an error, never as no sellers. "
            "LATENCY is SECONDS: typically 4-12s (one page ~4s; a long list walks every "
            "page). MARKETPLACES us, uk, de, ca, au, fr, it, es, jp, mx, br (no Walmart). "
            "COST API key required (the free no-signup lane cannot run live fetches). 0.5 "
            "credit when the answer carries at least one offer; a no-offers answer, an ASIN "
            "Amazon does not have, a barcode nothing resolves and a failed or busy fetch are "
            "never billed."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "asin": {
                    "type": "string",
                    "description": (
                        "The product's 10-character Amazon ASIN (a print book's ISBN-10 works "
                        "too). Provide asin or gtin."
                    ),
                },
                "gtin": {
                    "type": "string",
                    "description": (
                        "A barcode instead of an ASIN: UPC-12, EAN-13, GTIN-14 or ISBN-13. "
                        "Resolved cheapest evidence first: a listing we observe that carries "
                        "it, a book's ISBN-10, the same product on another Amazon "
                        "marketplace, then Amazon's own search (organic results only). "
                        "gtin_resolution says which, and barcode_verified whether the listing "
                        "itself carries the barcode. A barcode nothing resolves is never "
                        "billed."
                    ),
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "fr", "it", "es", "jp", "mx", "br"],
                    "default": "us",
                    "description": "The Amazon marketplace to read the offers page on.",
                },
                "include_used": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "true also lists the used, refurbished, open-box and collectible "
                        "offers in current_sellers.sellers. Either way current_sellers "
                        "carries used_offer_count, lowest_new and lowest_used, and every row "
                        "its condition. Not billed extra."
                    ),
                },
                "zip": {
                    "type": "string",
                    "description": (
                        "Optional (2026-10-14): a US 5-digit ZIP - the offers page as Amazon "
                        "shows it to a shopper at that ZIP, with location (Amazon's confirmed "
                        "'Deliver to' answer) and deliverable (whether the item is offered to "
                        "that ZIP right now; Amazon Fresh and Whole Foods items deliver only "
                        "to some ZIPs, and an out-of-area ZIP shows the same unavailable box "
                        "as a stock-out). Page 1 of the offers only, a one-off session, "
                        "nothing stored. country=us only. 1 credit when the answer carries an "
                        "offer; a ZIP Amazon rejects is guidance, never billed."
                    ),
                },
            },
            "anyOf": [
                {
                    "required": ["asin"],
                },
                {
                    "required": ["gtin"],
                },
            ],
        },
        "annotations": {
            "title": "Amazon Offers (live)",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    },
    {
        "name": "brand",
        "description": (
            "Amazon BRAND dossier from Logimu's own buy-box observations (derived "
            "intelligence, not estimates): catalog size, how many sellers win the buy box, "
            "control score (share of buy-box days won by FBA offers), winner diversity, "
            "Amazon's own retail share, FBA penetration, seller concentration (HHI) and "
            "churn, seller-pressure trend grades, since when we have observed the brand, its "
            "dominant category with p25/p50/p75 benchmarks, and the top-10 sellers by "
            "observed buy-box days with their feedback records. USE WHEN the user asks who "
            "sells a brand, how contested / Amazon-dominated / FBA-heavy a brand is, whether "
            "a brand is gaining or losing sellers, or wants to vet a brand for wholesale / "
            "arbitrage / brand protection. OPTIONS: sellers=true adds the full seller list "
            "(25 per page, page=N); network=true adds the brand's SELLER MAP - the brands "
            "connected to it because the same third-party sellers win the buy box on both "
            "(edges weighted by shared sellers, one hop, max 50); history=true adds up to 24 "
            "calendar months (ASINs, sellers, buy-box days, price, rating). All 11 Amazon "
            "marketplaces, no Walmart. HONESTY: 'observed since' is our data horizon, not the "
            "brand's age; a 404 means we have not observed the brand (names are matched as "
            "Amazon prints them). COST: paid plan required (the tool is listed only for keys "
            "on a paid plan). 1 credit for the dossier, +0.5 once when history comes back "
            "non-empty, +1 per page of sellers, +1 for the network. Unknown brand: 0."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "Brand name as Amazon prints it (case-insensitive).",
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "fr", "it", "es", "jp", "mx", "br"],
                    "default": "us",
                    "description": "Amazon marketplace.",
                },
                "history": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Add history.monthly (up to 24 months). +0.5 credit when non-empty."
                    ),
                },
                "sellers": {
                    "type": "boolean",
                    "default": False,
                    "description": "Add the full seller list (25 per page). +1 credit per page.",
                },
                "page": {
                    "type": "integer",
                    "default": 1,
                    "description": "Seller-list page (with sellers=true).",
                },
                "network": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Add the seller map: connected brands + weighted edges. +1 credit."
                    ),
                },
                "network_limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Edges to return with network=true (1-50).",
                },
            },
            "required": ["brand"],
        },
        "annotations": {
            "title": "Brand dossier (observed)",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "category",
        "description": (
            "Amazon CATEGORY landscape from Logimu's observations: size (ASINs, brands, "
            "sellers), pricing and rating averages, Amazon's own retail share, FBA "
            "penetration, Amazon private-label share, seller concentration (HHI top-5), heat "
            "(competitive intensity), 30-day catalog churn, demand signals "
            "(bought-past-month, revenue signal, velocity tier), root-level benchmark "
            "percentiles, the sub-categories and - for root categories - the top-10 brands by "
            "observed buy-box days. USE WHEN the user asks how competitive / Amazon-dominated "
            "/ FBA-heavy a category is, how big it is, which brands lead it, or wants to size "
            "a private-label or wholesale entry. Give category_id (Logimu's category id - the "
            "one every search result carries; or node_id for an Amazon browse-node id) OR q "
            "(a name fragment, English alias included) - with q the tool first returns "
            "matching categories (free) so you can pick the id - OR list=true to walk the "
            "taxonomy (the marketplace's root categories, or the children of parent_id; "
            "free). history=true adds months of products / brands / sellers. All 11 Amazon "
            "marketplaces. COST: paid plan required (listed only for keys on a paid plan). 1 "
            "credit per category profile, +0.5 with non-empty history; the name lookup and "
            "the taxonomy listing are free; unknown id: 0."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category_id": {
                    "type": "integer",
                    "description": (
                        "Logimu category id (warehouse id, as returned by every search result "
                        "and listing)."
                    ),
                },
                "node_id": {
                    "type": "integer",
                    "description": "Instead of category_id: the Amazon browse-node id.",
                },
                "q": {
                    "type": "string",
                    "description": (
                        "Instead of an id: part of a category name or path (English alias "
                        "included) - returns candidate categories, free."
                    ),
                },
                "list": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Walk the taxonomy: the marketplace's root categories, or the "
                        "children of parent_id. Free."
                    ),
                },
                "parent_id": {
                    "type": "integer",
                    "description": (
                        "With list=true: list this category's children instead of the roots."
                    ),
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "fr", "it", "es", "jp", "mx", "br"],
                    "default": "us",
                    "description": "Amazon marketplace.",
                },
                "history": {
                    "type": "boolean",
                    "default": False,
                    "description": "Add history.monthly. +0.5 credit when non-empty.",
                },
            },
        },
        "annotations": {
            "title": "Category landscape (observed)",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "market_lists",
        "description": (
            "Ranked LISTS from Logimu's observations, 25 per page: kind=brand_movers (brands "
            "gaining or losing distinct buy-box sellers fastest over 30 or 90 days), "
            "seller_movers (sellers whose buy-box footprint grew or shrank most), top_brands "
            "(brands ranked by observed buy-box days / sellers / control_score / asins / "
            "revenue / amazon_share, optionally within a root category_id), top_sellers "
            "(third-party sellers ranked by brands / buybox_days / asins / revenue - the "
            "cross-brand operators), top_categories (categories ranked by asins / brands / "
            "heat / revenue / price / sellers, root categories by default, or the children of "
            "parent_id). USE WHEN the user wants to DISCOVER brands, sellers or categories "
            "rather than look one up - sourcing leads, brands under seller pressure, the "
            "biggest resellers, which categories are hot. Then drill in with the brand / "
            "seller / category tools. All 11 Amazon marketplaces. COST: paid plan required "
            "(listed only for keys on a paid plan), 1 credit per page of 25 rows returned (an "
            "empty page is free). Daily cap per key on the derived family (default 2,000 "
            "calls)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "kind": {
                    "type": "string",
                    "enum": [
                        "brand_movers",
                        "seller_movers",
                        "top_brands",
                        "top_sellers",
                        "top_categories",
                    ],
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "fr", "it", "es", "jp", "mx", "br"],
                    "default": "us",
                    "description": "Amazon marketplace.",
                },
                "window": {
                    "type": "integer",
                    "enum": [30, 90],
                    "default": 30,
                    "description": "movers: comparison window in days.",
                },
                "direction": {
                    "type": "string",
                    "enum": ["up", "down"],
                    "default": "up",
                    "description": "movers: gaining (up) or losing (down).",
                },
                "sort": {
                    "type": "string",
                    "description": "top_*: the ranking field (see description).",
                },
                "category_id": {
                    "type": "integer",
                    "description": "top_brands: root category id to narrow to.",
                },
                "parent_id": {
                    "type": "integer",
                    "description": (
                        "top_categories: list this category's children instead of roots."
                    ),
                },
                "page": {"type": "integer", "default": 1},
            },
            "required": ["kind"],
        },
        "annotations": {
            "title": "Market lists (observed)",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "keywords",
        "description": (
            "Amazon's OWN autocomplete suggestion lists for a seed term, from Logimu's "
            "continuous harvest (since Aug 2026, 11 marketplaces): up to 6 lists - one per "
            "crawled prefix / department - each term with its position 1-10 WITHIN that list, "
            "when it was first and last observed and the marketplaces it was observed in, "
            "plus related observed vocabulary starting with the seed. history=true adds every "
            "observation of each list since the harvest began (a term entering, leaving or "
            "moving position). compare='us,uk,de' instead returns the seed's primary list on "
            "each marketplace and a matrix of positions per marketplace. USE WHEN the user "
            "asks what buyers type for X, wants listing / backend keyword language, seeds for "
            "product research, or how a term's suggestions differ by country. NOT volume "
            "figures (Amazon publishes none for its suggestions and none are implied), NOT a "
            "product-ranking map - for products pass a term to the shopping tool. Positions "
            "are comparable only within one list. COST: paid plan required (listed only for "
            "keys on a paid plan), 1 credit per lookup or compare, +0.5 with history when at "
            "least one closed observation exists; an unknown seed is free. Counts against the "
            "derived daily cap (default 2,000 calls per key)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "seed": {
                    "type": "string",
                    "description": (
                        "A seed term or prefix, at least 3 characters, e.g. 'electric "
                        "toothbrush'."
                    ),
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "fr", "it", "es", "jp", "mx", "br"],
                    "default": "us",
                    "description": "Amazon marketplace (ignored when compare is given).",
                },
                "history": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Also return each list's observation history (+0.5 credit when a "
                        "closed observation exists)."
                    ),
                },
                "compare": {
                    "type": "string",
                    "description": (
                        "Comma-separated marketplaces to compare instead of one lookup, e.g. "
                        "'us,uk,de' (2-11)."
                    ),
                },
            },
            "required": ["seed"],
        },
        "annotations": {
            "title": "Keyword suggestions (observed)",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "track_product",
        "description": (
            "TRACK a product: pin an Amazon ASIN into our hot lane so its all-offers page is "
            "re-read every hour or every 2, 4, 12 or 24 hours, for as long as the plan is "
            "active (or a ttl_days you set), with e-mail and webhook alerts on the thresholds "
            "you give; every read lands in the product's history as a sub-daily buy-box point "
            "(price, buy-box seller, fulfillment, offer count - buybox_price_points_hot on "
            "the product tool). USE WHEN the user wants to watch a product's price, buy box "
            "or seller count more often than our normal cadence: repricing, MAP and buy-box "
            "monitoring, a competitor's listing, a launch, a deal. Posting the same ASIN "
            "again renews it and changes its interval. DON'T USE to read data (product, "
            "offers): tracking only schedules the reads. COST 0 credits: what a plan sells is "
            "a daily allowance of tracked snapshots (Solo 2,500 a day = 416 products every 4 "
            "hours, Starter 6,000, Growth 18,000, Standard 40,000, Scale 170,000, Volume "
            "710,000); when the allowance is spent the answer says so with the upgrade link, "
            "and when only a longer interval fits it is granted (granted_interval). RETURNS "
            "id, asin, country, status (active / paused / expired / stopped), interval, "
            "granted_interval, requested_interval, snapshots_per_day, expires_at, in_lane, "
            "last_snapshot_at, next_due_at, pending (true until the lane picks it up, within "
            "~10 minutes), allowance (plan, snapshots_per_day, used, remaining). action=stop "
            "ends a tracking at once (by id from list_tracked, or by asin + country) and "
            "releases its allowance; the row stays listed 30 days as stopped. BULK "
            "(2026-10-14): asins (up to 1,000) with action=track / stop, and action=sync to "
            "make the active set equal to a list (dry_run first). STOCK STATES: every read is "
            "in_stock (a buy box), no_buybox (offers, no featured offer) or out_of_stock (no "
            "offers, confirmed twice); availability_change / out_of_stock / back_in_stock "
            "alert on the transitions, price alerts compare buy-box prices only. Paid plans "
            "only (the allowance belongs to a subscription). MARKETPLACES us, uk, de, ca, au, "
            "fr, it, es, jp, mx, br (no Walmart)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["track", "stop", "sync"],
                    "default": "track",
                    "description": (
                        "track (default) creates or renews the tracking(s); stop ends one or "
                        "many at once; sync (2026-10-14) makes the key's active set on one "
                        "marketplace EQUAL to asins: missing ones are created, active ones "
                        "not listed are stopped, the rest are left as they are - dry_run "
                        "first to see the counts."
                    ),
                },
                "id": {
                    "type": "integer",
                    "description": (
                        "With action=stop: the tracking id (from list_tracked). Or give asin "
                        "+ country, or ids / asins."
                    ),
                },
                "ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": (
                        "With action=stop: several tracking ids at once (up to 1,000)."
                    ),
                },
                "asin": {
                    "type": "string",
                    "description": (
                        "The product's 10-character Amazon ASIN (one product). Or give asins."
                    ),
                },
                "asins": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Bulk (2026-10-14): up to 1,000 ASINs in one call - with action=track "
                        "all get the same interval / ttl_days / alerts (results[] in input "
                        "order: created / renewed / refused / invalid, the allowance consumed "
                        "in input order, never all-or-nothing); with action=stop they are "
                        "stopped; with action=sync they are the full list the active set "
                        "becomes."
                    ),
                },
                "dry_run": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "With action=sync: return what would be created and stopped without "
                        "writing."
                    ),
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "fr", "it", "es", "jp", "mx", "br"],
                    "default": "us",
                    "description": "The Amazon marketplace to track the product on.",
                },
                "interval": {
                    "type": "string",
                    "enum": ["1h", "2h", "4h", "12h", "24h"],
                    "default": "4h",
                    "description": (
                        "How often the lane re-reads the all-offers page. A shorter interval "
                        "costs more of the daily allowance (1h = 24 snapshots a day, 2h = 12, "
                        "4h = 6, 12h = 2, 24h = 1)."
                    ),
                },
                "ttl_days": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 365,
                    "description": (
                        "Optional: stop after this many days (1-365). Omit (or 0) and the "
                        "tracking runs for as long as the plan is active - a lapsed plan "
                        "keeps it 7 days, then it pauses and resumes with the plan."
                    ),
                },
                "alert_email": {
                    "type": "string",
                    "description": (
                        "Optional: e-mail alerts for the notify_if thresholds - 'true' for "
                        "the account's own address, or an address. One e-mail per event, at "
                        "most 50 a day per tracking. 'false' detaches. Works with or without "
                        "webhook_url."
                    ),
                },
                "webhook_url": {
                    "type": "string",
                    "description": (
                        "Optional: an https URL Logimu POSTs to when a notify_if threshold "
                        "fires on a new observation (signed X-Logimu-Signature: "
                        "sha256=HMAC-SHA256(secret, body); the secret is returned once in "
                        "webhook_secret). An empty string detaches it."
                    ),
                },
                "notify_if": {
                    "type": "object",
                    "description": (
                        "With webhook_url and / or alert_email: the thresholds. price_below / "
                        "price_above (a buy-box price), price_change_pct (percent move of the "
                        "buy-box price since the last in-stock read), buybox_seller_change "
                        "(true: a different seller holds the buy box, between two in-stock "
                        "reads), offer_count_below / offer_count_above (a count), "
                        "availability_change (true: the stock STATE changed - in_stock, "
                        "no_buybox = offers exist but Amazon shows no featured offer, "
                        "out_of_stock = no offers at all, confirmed by a second read; the "
                        "event carries both codes), out_of_stock (true: shorthand for a "
                        "change to out_of_stock), back_in_stock (true: a change to in_stock). "
                        "{} attaches the webhook and fires on nothing."
                    ),
                    "properties": {
                        "price_below": {"type": "number"},
                        "price_above": {"type": "number"},
                        "price_change_pct": {"type": "number"},
                        "buybox_seller_change": {"type": "boolean"},
                        "offer_count_below": {"type": "integer"},
                        "offer_count_above": {"type": "integer"},
                        "availability_change": {"type": "boolean"},
                        "out_of_stock": {"type": "boolean"},
                        "back_in_stock": {"type": "boolean"},
                    },
                },
            },
            "anyOf": [
                {
                    "required": ["asin"],
                },
                {
                    "required": ["asins"],
                },
                {
                    "required": ["id"],
                },
                {
                    "required": ["ids"],
                },
            ],
        },
        "annotations": {
            "title": "Track a product (hot lane)",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "list_tracked",
        "description": (
            "LIST the products this API key tracks (track_product): each with its status, "
            "interval, expiry, whether the hot lane has picked it up, the lane's last and "
            "next read, plus the plan's tracking allowance (snapshots a day: total, used, "
            "remaining). USE WHEN the user asks what is being tracked, whether a tracking is "
            "live, how much allowance is left, or wants to stop one (the id goes to DELETE "
            "/v1/track/{id} on the REST API). Stopped trackings stay listed for 30 days. COST "
            "0 credits. Paid plans only."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "fr", "it", "es", "jp", "mx", "br"],
                    "description": (
                        "Only this marketplace's trackings (default: every marketplace)."
                    ),
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "paused", "expired", "stopped"],
                    "description": "Only trackings in this state (default: all, newest first).",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000,
                    "default": 200,
                    "description": "Maximum rows to return.",
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "Rows to skip (paging; total says how many there are).",
                },
                "events_for": {
                    "type": "integer",
                    "description": (
                        "A tracking id: return that tracking's webhook events instead of the "
                        "list - which notify_if threshold fired on which observation, the "
                        "payload, and the delivery state (pending / delivered / failed, "
                        "attempts, last error)."
                    ),
                },
            },
        },
        "annotations": {
            "title": "Tracked products",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "batch",
        "description": (
            "BATCHES: run any Logimu endpoint over a whole list in one job and come back for "
            "the results - the same batch API as REST /v1/batches (see "
            "https://api.logimu.com/docs#batch). action=estimate prices a list before "
            "anything is billed (free); action=create makes a named, re-runnable batch (add "
            "start=true to launch its first run at once); action=run launches a run of an "
            "existing batch; action=status reports a batch (runs, line stats) or, with "
            "run_id, one run's progress (rows done, credits so far, queue position); "
            "action=results returns completed result rows of a run, mid-run too (limit / "
            "offset to page; jsonl_url and csv_url give the full download); action=list lists "
            "the key's batches; action=schedule repeats a batch daily / weekly / monthly "
            "(credit_ceiling, webhook_url); action=delete removes a batch. USE WHEN the user "
            "has more than a handful of ASINs, barcodes, search terms, seller ids, brands or "
            "seeds to run, wants a daily/weekly refresh, or wants a CSV. Kinds: product "
            "(asins or gtins - or source=tracked for the ASINs this key tracks, typically "
            "with include [history_only] at 0.05 a row), search (terms, live SERP), seller / "
            "brand / category / keywords (paid plans), and every other endpoint as its own "
            "kind (shopping, warehouse_search, bestsellers, seller_products, seller_brands, "
            "seller_network, brand_sellers, brand_network, keywords_compare, categories, "
            "category_search, brands_top, brands_movers, sellers_top, sellers_movers, "
            "categories_top) with the endpoint's query parameters in params. Each row bills "
            "what the endpoint bills; failed, not-found and duplicate rows are never billed; "
            "runs are serialized per marketplace. COST estimate / status / results / list are "
            "free; create + run queue billable rows (the estimate is the ceiling). API key "
            "required (keyed lanes)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "estimate",
                        "create",
                        "run",
                        "status",
                        "results",
                        "list",
                        "schedule",
                        "delete",
                    ],
                    "description": "What to do (see the tool description).",
                },
                "batch_id": {
                    "type": "integer",
                    "description": "For run / status / results / schedule / delete.",
                },
                "run_id": {
                    "type": "integer",
                    "description": "For status (one run's progress) and results.",
                },
                "name": {
                    "type": "string",
                    "description": "create: the batch's name (1-120 characters).",
                },
                "kind": {
                    "type": "string",
                    "default": "product",
                    "description": (
                        "estimate / create: product (default), search, seller, brand, "
                        "category, keywords, or any endpoint kind named in the description."
                    ),
                },
                "country": {
                    "type": "string",
                    "default": "us",
                    "description": (
                        "estimate / create: us, uk, de, ca, au, fr, it, es, jp, mx, br, "
                        "walmart (search batches Amazon only)."
                    ),
                },
                "mode": {
                    "type": "string",
                    "enum": ["cache", "live", "auto"],
                    "description": (
                        "product / seller batches: cache = warehouse only, live = scrape "
                        "every row, auto = warehouse when fresh enough (required on create "
                        "for product batches)."
                    ),
                },
                "max_age_days": {"type": "integer", "minimum": 1, "maximum": 365, "default": 30},
                "asins": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "product batches: the ASINs (or Walmart item ids).",
                },
                "gtins": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "product batches: barcodes instead of ASINs.",
                },
                "source": {
                    "type": "string",
                    "enum": ["tracked"],
                    "description": (
                        "product batches: tracked = the ASINs this key tracks on the "
                        "marketplace instead of a list."
                    ),
                },
                "terms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "search / shopping / warehouse_search / category_search batches: the "
                        "queries."
                    ),
                },
                "seller_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "seller, seller_products, seller_brands, seller_network batches."
                    ),
                },
                "brands": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "brand, brand_sellers, brand_network batches.",
                },
                "category_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "category / categories batches (ids, or root).",
                },
                "seeds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "keywords / keywords_compare batches: seed terms.",
                },
                "urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "bestsellers batches: Best Sellers URLs.",
                },
                "pages": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 40,
                    "description": (
                        "search batches: pages per term (1-3); ranked-list batches: pages of "
                        "25 rows (1-40)."
                    ),
                },
                "params": {
                    "type": "object",
                    "description": (
                        "endpoint kinds: the endpoint's query parameters, fixed for every "
                        "row."
                    ),
                },
                "include": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Extras: history (seller / brand / category / keywords), reviews, "
                        "used, offer_history, bsr_history, history_only (product), blocks "
                        "(search)."
                    ),
                },
                "history_sellers": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                },
                "history_points": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20000,
                    "default": 500,
                },
                "start": {
                    "type": "boolean",
                    "default": False,
                    "description": "create: also launch the first run at once.",
                },
                "schedule": {
                    "type": "string",
                    "enum": ["none", "daily", "weekly", "monthly"],
                    "description": (
                        "schedule: how often the batch re-runs (none stops the schedule)."
                    ),
                },
                "schedule_enabled": {
                    "type": "boolean",
                    "default": True,
                    "description": "schedule: pause without deleting.",
                },
                "credit_ceiling": {
                    "type": "number",
                    "description": (
                        "schedule: a firing whose fresh estimate exceeds this does not run "
                        "(email instead); default 2x the estimate."
                    ),
                },
                "webhook_url": {
                    "type": "string",
                    "description": (
                        "schedule: POSTed on run completion / pause, HMAC-SHA256 signed; the "
                        "secret is returned once."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 50,
                    "description": (
                        "results: rows to return (page with offset; the download URLs carry "
                        "everything)."
                    ),
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "results: rows to skip.",
                },
            },
            "required": ["action"],
        },
        "annotations": {
            "title": "Batches (bulk and scheduled runs)",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    },
    {
        "name": "account",
        "description": (
            "ACCOUNT: the calling key's balance, plan, 30-day usage by endpoint and its "
            "product-tracking allowance (snapshots a day: total, used, remaining) - the same "
            "as REST GET /v1/account. USE WHEN the user asks how many credits are left, what "
            "a job will leave, what the key has been used for, or how much tracking room "
            "there is. COST free, never billed. API key required (keyed lanes); without one, "
            "nothing to report."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
        "annotations": {
            "title": "Account balance and usage",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
]

POINTER = (
    "This is the introspection stub. The live server is hosted at "
    f"{HOSTED} — add it to your MCP client as a remote (Streamable HTTP) "
    "connector. Free, no signup: 30 queries/day. Unlimited use, full history and "
    "live scrapes: a paid-plan API key (from $19/month) at https://api.logimu.com"
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
