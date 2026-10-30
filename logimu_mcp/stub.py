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
    "version": "1.13.0",
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
            "price_history and stock_history back to first observation, change events tagged "
            "with the buy-box seller at each change, the current all-seller offer table with "
            "30-day buy-box days (each seller row carries fulfillment AMZ/FBA/FBM and "
            "delivery days), a fulfillment block (buy-box AMZ/FBA/FBM, offer counts, whether "
            "Amazon sells and holds the buy box, buy-box delivery days and dispatch latency), "
            "the bought-past-month badge (measured aggregate buyer behavior, not an "
            "estimate), brand stats, and since 2026-09-27: dimensions (item weight + package "
            "size as printed plus parsed metric weight_g / *_cm), deal_history (list price, "
            "savings and coupon/promotion text as segments of consecutive observations, with "
            "a current view), bought_past_month_history (the badge over time; null = page "
            "seen without a badge), rating_history (rating_count + rating per observed day "
            "with ratings_gained_30d/90d), and variation_coverage (the variation matrix as "
            "last seen with, per child, whether we track it and its latest 30-day price - "
            "current state, not history). With offer_history=true every per-seller point also "
            "carries that day's shipping cost, fba and prime, and the answer carries "
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
            "last_fetched_at, read = which page it reads) or null. Since 2026-10-29 every "
            "Amazon answer also carries bsr_points_hot: every sales-rank reading of the last "
            "30 days, newest last, {observed_at, bsr, bsr_category, bsr_leaf, "
            "bsr_leaf_category}, one per product-page read that showed a rank (bsr_history "
            "keeps one per day; null when none; history_only carries it too). Since "
            "2026-10-15 Amazon answers carry buybox_condition (new | used | null = no "
            "featured offer; with buybox_condition_source product_page | offers_page and "
            "buybox_condition_detail: the pinned offer's condition text, used_only_buybox, or "
            "the used storefront's name - Amazon Resale / Amazon Warehouse win the buy box "
            "like any seller and read as Amazon retail before), buybox_state (what the lane's "
            "newest all-offers read saw: in_stock | no_buybox | out_of_stock, with "
            "buybox_state_observed_at and stock_state_source when it decided stock_state; "
            "stock_state, in_stock and out_of_stock always agree), and on LIVE answers "
            "variation_status (page_is_sibling | page_is_other | null) + page_asin when "
            "Amazon served another ASIN's page for the one asked (cache answers: null); "
            "unit_price on LIVE answers = Amazon's per-unit price of price where the page "
            "prints one ({symbol, value, currency, raw, per}; null otherwise); with "
            "full_offers, offers_complete (false = the offers pages stopped part-way, "
            "offers_partial_reason says why). Amazon answers also carry the observed "
            "product-page content, the byline (authors[] with role_norm "
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
            "reads live. COST paid plans only: the user signs in with their Logimu account or "
            "passes an API key (the no-signup lane has the shopping tool only). 0.5 credits "
            "from cache with everything included - bsr_history and offer_history too, no "
            "extra charge since 2026-10-10 - and 1 for a live scrape (2 on Walmart); "
            "history_only=true returns just the history series (rank, offers, buy-box price, "
            "rating_history) for 0.05 credit. Misses and partial scrapes are never billed; a "
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
                        "than max_age_days, otherwise scrape."
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
                        "into our hot lane, which re-reads its all-offers page (or, with "
                        "read=product_page, its product page) every `interval` for 30 days "
                        "and adds every read to buybox_price_points_hot - the same as the "
                        "track_product tool. No extra credits (the plan's daily "
                        "tracked-snapshot allowance is drawn); the answer is served even when "
                        "the tracking is refused and its `track` block says why. Amazon only."
                    ),
                },
                "interval": {
                    "type": "string",
                    "enum": ["1h", "2h", "4h", "12h", "24h"],
                    "default": "4h",
                    "description": (
                        "With track=true: how often the lane re-reads the product (1h = 24 "
                        "snapshots a day)."
                    ),
                },
                "read": {
                    "type": "string",
                    "enum": ["offers", "product_page"],
                    "default": "offers",
                    "description": (
                        "With track=true (2026-10-29): offers (default) re-reads the "
                        "all-offers page; product_page re-reads the product page and its "
                        "offers page, so every reading's sales rank lands in bsr_points_hot. "
                        "A product-page read draws 2 snapshots of the allowance."
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
            "ca, au, fr, it, es, jp, mx, br, walmart. COST without signup 1 of 5 daily "
            "queries, without detail (detail=true needs a paid plan). Keyed: 2 credits, or 5 "
            "with detail=true. Empty result sets are never billed. detail=true attaches to "
            "EVERY product everything the basic product call carries (2026-09-28): current "
            "sellers with fulfillment and delivery, 30-day price/stock events, stock history, "
            "brand_stats, dimensions, deal/badge/rating history, variation coverage, page "
            "content and up to 100 featured reviews, plus a response-wide seller_ratings "
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
            "universe, not the entire Amazon catalog. COST paid plans only (sign in or an API "
            "key; the no-signup lane has the shopping tool only). 1 credit per 25 rows "
            "returned. Empty result sets are never billed. SELLER FEEDBACK (2026-09-18): the "
            "response also carries seller_ratings - a separate array with "
            "seller_positive_pct, seller_feedback_count, seller_rating and observed_at for "
            "every buy-box seller named in the rows (Amazon marketplaces; absent on Walmart). "
            "Row shapes are unchanged. Not billed."
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
                    "description": "Maximum rows to return (up to 100).",
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
            "link, image, rating, ratings_total, price, list_price, unit_price (Amazon's "
            "per-unit price, where the card prints one, never the price), recent_sales badge, "
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
            "never billed. ZIP (2026-10-29, country=us only): pass zip (a US 5-digit ZIP) to "
            "search as a shopper at that ZIP sees it - a plain search at a city ZIP lists the "
            "local stores' items (Whole Foods, Amazon Fresh, local partners) beside shipped "
            "ones; store=wholefoods|fresh runs Amazon's own storefront search for that "
            "store's assortment at the ZIP. USE WHEN the user asks what a recipient at a ZIP "
            "can buy (groceries, same-day items), which store carries a query locally, or "
            "delivery fees / windows / minimums per item. The answer adds location (the "
            "result page's confirmed 'Deliver to'), store, empty_reason (null with results; "
            "no_results_at_zip or store_nothing_for_query_at_zip - the latter cannot tell a "
            "store that skips the ZIP from one with no match for the query), observed_at and "
            "request_metadata.zip_session (new | reused: a session at a ZIP is kept a few "
            "minutes per account, so a follow-up search or an offers zip= check on the same "
            "ZIP is fast). Per result: store (from the card's own store link, never guessed), "
            "delivery (Amazon's line as printed), delivery_terms {fee, window, free_over, "
            "membership, pickup, fastest, non_member} - the terms Amazon shows a signed-out "
            "shopper, Prime included; a field the line does not state is null, and NEVER "
            "report free delivery from a missing fee - and stock {state: "
            "in_stock|low_stock|out_of_stock|null, left} (null = the card shows no price and "
            "no stock line, availability unknown: check it with offers zip=). Results and "
            "their order are Amazon's own; this is discovery, not a stock check: confirm an "
            "item with offers zip= before the user buys. At most 3 pages a call. LATENCY "
            "typically 5-10 s for the first search at a ZIP, up to about a minute when Amazon "
            "challenges new sessions; about 1-2 s for a follow-up on the same ZIP. BILLING at "
            "a ZIP: 1 credit per page fetched, a VERIFIED empty page included (Amazon's own "
            "no-results text on a page that confirmed the ZIP, empty_reason set) - the one "
            "exception to 'empty never bills'; a block, a checkpoint page, an unconfirmed ZIP "
            "or no answer is a failure, never an empty answer, never billed; a ZIP Amazon "
            "rejects is guidance, never billed."
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
                "zip": {
                    "type": "string",
                    "description": (
                        "Optional (2026-10-29): a US 5-digit ZIP - the search as a shopper at "
                        "that ZIP sees it, with the local stores' items, each result's store, "
                        "delivery_terms and stock, and the page's confirmed location. "
                        "country=us only; at most 3 pages a call. A verified empty answer "
                        "(empty_reason set) is billed 1 credit. ZIP+4 is cut to 5 digits."
                    ),
                },
                "store": {
                    "type": "string",
                    "enum": ["wholefoods", "fresh"],
                    "description": (
                        "Optional, with zip only: Amazon's own storefront search for that "
                        "store's assortment at the ZIP (Whole Foods Market or Amazon Fresh). "
                        "A local partner such as Lucky is reached through refinements with "
                        "its p_n_alm_brand_id value. Cannot be combined with category_id."
                    ),
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
            "buybox_seller_id, seller_count, no_sellers, pages_fetched, complete (false = "
            "Amazon stopped serving the offers pages part-way: the list is the part read, "
            "with partial_reason and a note), buybox_condition / buybox_condition_source / "
            "buybox_condition_detail (new | used | null = no featured offer; the pinned "
            "offer's condition text or the used storefront's name, e.g. Amazon Resale), "
            "current_sellers (sellers[] buy box first, then price ascending: seller, "
            "seller_id, price, shipping_cost, condition, condition_class, is_buybox, is_fba, "
            "is_prime, fulfillment, ships_from, delivery, seller_rating, plus buybox_days_30d "
            "and the 30-day buy-box shares from our observations; offer_count, "
            "used_offer_count, lowest_new, lowest_used), fulfillment (offer counts by AMZ / "
            "FBA / FBM, whether Amazon sells or holds the buy box) and seller_ratings; with "
            "gtin also gtin_resolution (source, confidence, barcode_verified). HONESTY: "
            "no_sellers=true means Amazon lists no offer for the product right now, an answer "
            "confirmed by a second, independent fetch before it is served; a fetch that fails "
            "is reported as an error, never as no sellers. LATENCY is SECONDS: typically "
            "4-12s (one page ~4s; a long list walks every page). MARKETPLACES us, uk, de, ca, "
            "au, fr, it, es, jp, mx, br (no Walmart). COST API key required (the free "
            "no-signup lane cannot run live fetches). 0.5 credit when the answer carries at "
            "least one offer; a no-offers answer, an ASIN Amazon does not have, a barcode "
            "nothing resolves and a failed or busy fetch are never billed."
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
                        "offer, and (since 2026-10-29) for a verified not-deliverable answer "
                        "(the ZIP confirmed on the page, the offers page read, zero offers: "
                        "not_deliverable_verified true); a ZIP Amazon rejects is guidance, "
                        "never billed, as are deliverable null, a 404 and a failed fetch. A "
                        "session at a ZIP is kept a few minutes per account, so this check "
                        "right after a serp zip= search on the same ZIP skips the warm-up."
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
        "name": "deals",
        "description": (
            "LIVE Amazon Today's Deals: the deals page of one marketplace, read from Amazon "
            "at request time and filtered the way Amazon's own page filters it - department "
            "(category_id), deal collection (deal_types: lightning_deal, trending, coupons, "
            "started_today, ending_today; or any collection id an answer lists), percent off, "
            "price, Prime Exclusive, minimum rating, brand. USE WHEN the user asks what is on "
            "sale or discounted on Amazon right now, wants today's deals or lightning deals "
            "in a department, deals above a discount or under a price, coupon deals, or deals "
            "ending today. DON'T USE for one product's price history or past price drops "
            "(product with offer_history), for who sells a product right now (offers), for a "
            "keyword search (serp, shopping) or for what sells best in a category "
            "(bestsellers). RETURNS deals[] (position, asin, title, link, image, deal_id, "
            "deal_link, deal_type e.g. BEST_DEAL / LIGHTNING_DEAL, is_lightning_deal, "
            "deal_state, percent_claimed, ends_at, deal_price and list_price {value, "
            "currency, symbol, label}, percent_off, savings, deal_badge, is_prime_price, "
            "coupon {text, amount, promotion_id, link}, brand, brand_id, department_ids, "
            "product_group, product_type, variations), categories[] (category_id, name, "
            "selected: the departments to pass back as category_id), collections[] (id, name: "
            "pass back as collection), facets (brands with ids, reviewRating, price and "
            "percentOff ranges, accessType), selected_filters, filter_check (per requested "
            "filter: applied / not_applied / unverified), pagination (page, page_size, "
            "pages_fetched, start_index, returned, has_more, partial), amazon "
            "(marketplace_id, locale, currency), observed_at and cached. HONESTY: an empty "
            "deals list is a real answer (e.g. no lightning deals running at this hour); a "
            "filter Amazon did not apply (filter_check not_applied, e.g. a category_id that "
            "is not one of the marketplace's deals departments) is refused as an error, never "
            "billed, instead of serving the unfiltered page; unverified filters are served, "
            "so say so before relying on them; there is no total count (has_more says whether "
            "the last page came back full) and no deal start time; ends_at only where Amazon "
            "shows a countdown; list_price is Amazon's reference price with its own label "
            "(RRP, Was, Typical ...), null when the page shows none. LATENCY is SECONDS: "
            "~10-30s a page (pages=5 up to ~2 min); an identical request within 15 min may "
            "come from our cache in milliseconds. MARKETPLACES us, uk, de, ca, au, fr, it, "
            "es, jp, mx, br (no Walmart). COST API key required (the free no-signup lane "
            "cannot run live fetches). 1 credit per deals page fetched that returned at least "
            "one deal, whatever its size (30, 60, 90 or 120 deals are all 1 credit, so "
            "page_size=120 gives the most deals per credit), cached or fresh; a page with no "
            "deals, an empty list, a blocked or busy fetch and bad input are never billed."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "fr", "it", "es", "jp", "mx", "br"],
                    "description": (
                        "The Amazon marketplace whose deals page to read. Required unless url "
                        "is given; with url it must match the URL's marketplace."
                    ),
                },
                "url": {
                    "type": "string",
                    "description": (
                        "Optional: an Amazon deals URL (/deals, /events/deals or "
                        "/gp/goldbox). The host decides the marketplace and its query string "
                        "is kept (e.g. a filtered deals page copied from the browser)."
                    ),
                },
                "category_id": {
                    "type": "string",
                    "description": (
                        "A deals department id from categories[] of a previous answer (Amazon "
                        "applies one department at a time)."
                    ),
                },
                "deal_types": {
                    "type": "string",
                    "enum": [
                        "lightning_deal",
                        "trending",
                        "coupons",
                        "started_today",
                        "ending_today",
                    ],
                    "description": (
                        "One of Amazon's stable deal collections. Not together with "
                        "collection."
                    ),
                },
                "collection": {
                    "type": "string",
                    "description": (
                        "Any other collection id from collections[] of a previous answer "
                        "(collections differ per marketplace and over time). Not together "
                        "with deal_types."
                    ),
                },
                "discount": {
                    "type": "string",
                    "enum": [
                        "10_percent_off",
                        "25_percent_off",
                        "50_percent_off",
                        "70_percent_off",
                    ],
                    "description": (
                        "Rainforest form of min_discount (50_percent_off = at least 50% off). "
                        "Not together with min_discount."
                    ),
                },
                "min_discount": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "description": (
                        "Minimum percent off (0-100). Amazon applies it on the us, uk, de, "
                        "ca, au, mx, jp and br deals pages; amazon.it, amazon.fr and "
                        "amazon.es have no discount filter, so there it is refused "
                        "(not_applied, never billed): ask without it and filter on "
                        "percent_off."
                    ),
                },
                "max_discount": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "description": (
                        "Maximum percent off (0-100). Same marketplaces as min_discount "
                        "(refused on it, fr, es)."
                    ),
                },
                "min_price": {
                    "type": "number",
                    "minimum": 0,
                    "description": (
                        "Minimum deal price in the marketplace currency (Amazon applies whole "
                        "units; a fraction is rounded down)."
                    ),
                },
                "max_price": {
                    "type": "number",
                    "minimum": 0,
                    "description": (
                        "Maximum deal price in the marketplace currency (Amazon applies whole "
                        "units; a fraction is rounded up)."
                    ),
                },
                "prime_exclusive": {
                    "type": "boolean",
                    "default": False,
                    "description": "true = Prime Exclusive deals only.",
                },
                "minimum_rating": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 4,
                    "description": "Only products rated at least this many stars (1-4).",
                },
                "brand": {
                    "type": "string",
                    "description": (
                        "A brand id from facets.brands of a previous answer (e.g. "
                        "811979|dreame)."
                    ),
                },
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 400,
                    "default": 1,
                    "description": "1-based page of the deals list.",
                },
                "page_size": {
                    "type": "integer",
                    "enum": [30, 60, 90, 120],
                    "default": 60,
                    "description": (
                        "Deals per page; Amazon serves steps of 30 only. Every page is 1 "
                        "credit whatever its size, so 120 gives the most deals per credit."
                    ),
                },
                "pages": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                    "default": 1,
                    "description": (
                        "Consecutive pages merged into one answer, starting at page (stops "
                        "early on a short page). 1 credit per page that returned deals."
                    ),
                },
            },
            "anyOf": [
                {
                    "required": ["country"],
                },
                {
                    "required": ["url"],
                },
            ],
        },
        "annotations": {
            "title": "Amazon Today's Deals (live)",
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
            "empty page is free). Daily cap per account on the derived family (default 2,000 "
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
            "product-ranking map - which products appear on page 1 for a term is "
            "keyword_rankings, the keywords a product shows up for is product_keywords. "
            "Positions are comparable only within one list. COST: paid plan required (listed "
            "only for keys on a paid plan), 1 credit per lookup or compare, +0.5 with history "
            "when at least one closed observation exists; an unknown seed is free. Counts "
            "against the derived daily cap (default 2,000 calls per account)."
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
        "name": "keyword_rankings",
        "description": (
            "Page 1 of Amazon search for a keyword, as Logimu last OBSERVED it (head search "
            "terms taken from Amazon's own autocomplete, each observed about once a week, all "
            "departments; amazon.com from one US delivery ZIP): the organic order with "
            "product facts (title, brand, price, rating) and each product's latest observed "
            "buy box (seller, AMZ / FBA / FBM, other sellers), the sponsored units present in "
            "the page HTML (Sponsored Brands banners and videos, server-rendered Sponsored "
            "Products; ones Amazon loads later by JavaScript are counted as slots only), the "
            "Overall Pick (Amazon's Choice) holder, Amazon's result count, page_summary "
            "(organic slots by brand and by buy-box seller, Amazon's own buy boxes, FBA / "
            "FBM, Sponsored Brands units by brand) and the products that entered or left page "
            "1 since the previous observation, all dated. history=true adds every weekly "
            "observation and the rank series of the page's products. USE WHEN the user asks "
            "which products, brands or sellers hold page 1 for a search term, who advertises "
            "on it, or how the page changed. All 11 Amazon marketplaces (country). NOT volume "
            "figures (Amazon publishes none for search terms and none is implied) and NOT "
            "live: a dated weekly sample, and the same search minutes apart differs by a few "
            "products - for a live page use the serp tool, for what Amazon suggests for a "
            "seed the keywords tool, for the keywords a product shows up for "
            "product_keywords. A keyword outside the observed set is free "
            "(keyword_not_found). COST: paid plan required (listed only for keys on a paid "
            "plan); 1 credit (+0.5 with history when more than one observation exists). "
            "Counts against the derived daily cap (default 2,000 calls per account)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": (
                        "A search term, e.g. 'micro sd card 128gb high endurance' "
                        "(case-insensitive)."
                    ),
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "fr", "it", "es", "jp", "mx", "br"],
                    "default": "us",
                    "description": (
                        "Amazon marketplace: us (amazon.com, default), uk, de, ca, au, fr, "
                        "it, es, jp, mx or br, each searched in its own language. us and uk "
                        "are read in full about weekly; the other nine started 2026-10-29 / "
                        "10-30 and fill in week by week (coverage says how far)."
                    ),
                },
                "history": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Also return every weekly observation and the products' rank series; "
                        "+0.5 credit when more than one exists."
                    ),
                },
            },
            "required": ["keyword"],
        },
        "annotations": {
            "title": "Keyword rankings (observed)",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "product_keywords",
        "description": (
            "REVERSE ASIN on Amazon (11 marketplaces, country): every observed keyword (head "
            "search terms taken from Amazon's own autocomplete, page 1 observed about once a "
            "week) whose latest page 1 shows the product, organically with its rank or in a "
            "sponsored unit present in the page HTML, with the keyword's result count, the "
            "Overall Pick badge and the date; organic first, best rank first, with totals "
            "(keywords, organic, top 10, sponsored, Overall Pick). Pass asins (up to 10, the "
            "product first) to COMPARE it with competitors: each keyword row adds every "
            "competitor's organic rank, asins_on_page and gap (a competitor on page 1 "
            "organically, the product not); gaps=true keeps only those. history=true adds the "
            "first product's rank on each keyword over time. USE WHEN the user asks which "
            "keywords a product (theirs or a competitor's) shows up for, where competitors "
            "are visible and they are not, or how a product's position on a term moved. "
            "Coverage is head search terms and page 1 only (the coverage block gives the "
            "counts), so a product shows fewer keywords than a full search index would. NOT "
            "volume figures and NOT live: dated weekly samples. A product not seen on any "
            "observed page is free (asin_not_found). COST: paid plan required (listed only "
            "for keys on a paid plan); 1 credit per 25 keywords returned per ASIN compared "
            "(+0.5 with history when a keyword has more than one observation). Counts against "
            "the derived daily cap (default 2,000 calls per account)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "asin": {
                    "type": "string",
                    "description": (
                        "A 10-character Amazon ASIN: the keywords it shows up for. Give asin "
                        "OR asins."
                    ),
                },
                "asins": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 10,
                    "description": (
                        "Up to 10 ASINs, the product first, then the competitors to compare "
                        "it with."
                    ),
                },
                "country": {
                    "type": "string",
                    "enum": ["us", "uk", "de", "ca", "au", "fr", "it", "es", "jp", "mx", "br"],
                    "default": "us",
                    "description": (
                        "Amazon marketplace: us (amazon.com, default), uk, de, ca, au, fr, "
                        "it, es, jp, mx or br, each searched in its own language. us and uk "
                        "are read in full about weekly; the other nine started 2026-10-29 / "
                        "10-30 and fill in week by week (coverage says how far)."
                    ),
                },
                "placement": {
                    "type": "string",
                    "enum": ["all", "organic", "sponsored"],
                    "default": "all",
                    "description": (
                        "Organic and sponsored (default), organic only, or sponsored only."
                    ),
                },
                "gaps": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "With asins: only the keywords where a competitor is on page 1 "
                        "organically and the first product is not."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 50,
                    "description": "Keywords per answer (1 credit per 25 returned, per ASIN).",
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "Skip this many keywords (paging).",
                },
                "history": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Also return the first product's rank on each keyword in every "
                        "observation; +0.5 credit when a keyword has more than one."
                    ),
                },
            },
        },
        "annotations": {
            "title": "Keywords for a product (observed)",
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
            "the product tool). read=product_page (2026-10-29) reads the product page and its "
            "offers page instead, so the SALES RANK is read too: every reading lands in "
            "bsr_points_hot (and its offers page in buybox_price_points_hot); such a read "
            "draws 2 snapshots of the allowance. USE WHEN the user wants to watch a product's "
            "price, buy box, seller count or sales rank more often than our normal cadence: "
            "repricing, MAP and buy-box monitoring, a competitor's listing, a launch, a deal, "
            "a book's rank. Posting the same ASIN again renews it and changes its interval. "
            "DON'T USE to read data (product, offers): tracking only schedules the reads. "
            "COST 0 credits: what a plan sells is a daily allowance of tracked snapshots "
            "(Solo 2,500 a day = 416 products every 4 hours, Starter 6,000, Growth 18,000, "
            "Standard 40,000, Scale 170,000, Volume 710,000); when the allowance is spent the "
            "answer says so with the upgrade link, and when only a longer interval fits it is "
            "granted (granted_interval). RETURNS id, asin, country, status (active / paused / "
            "expired / stopped), interval, read, granted_interval, requested_interval, "
            "snapshots_per_day (reads_per_day too for product_page), expires_at, in_lane, "
            "last_snapshot_at, next_due_at, pending (true until the lane picks it up, within "
            "~10 minutes), allowance (plan, snapshots_per_day, used, remaining). action=stop "
            "ends a tracking at once (by id from list_tracked, or by asin + country) and "
            "releases its allowance; the row stays listed 30 days as stopped. BULK "
            "(2026-10-14): asins (up to 10,000) with action=track / stop, and action=sync to "
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
                        "many at once; sync (2026-10-14) makes the account's active set on "
                        "one marketplace EQUAL to asins: missing ones are created, active "
                        "ones not listed are stopped, the rest are left as they are - dry_run "
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
                        "With action=stop: several tracking ids at once (up to 10,000)."
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
                        "Bulk (2026-10-14): up to 10,000 ASINs in one call - with "
                        "action=track all get the same interval / ttl_days / alerts "
                        "(results[] in input order: created / renewed / refused / invalid, "
                        "the allowance consumed in input order, never all-or-nothing); with "
                        "action=stop they are stopped; with action=sync they are the full "
                        "list the active set becomes."
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
                        "How often the lane re-reads the product (see read). A shorter "
                        "interval costs more of the daily allowance (1h = 24 snapshots a day, "
                        "2h = 12, 4h = 6, 12h = 2, 24h = 1; twice that with "
                        "read=product_page)."
                    ),
                },
                "read": {
                    "type": "string",
                    "enum": ["offers", "product_page"],
                    "default": "offers",
                    "description": (
                        "Which page each read fetches (2026-10-29): offers (default) = the "
                        "all-offers page (buy box, price, every offer, stock); product_page = "
                        "the product page and its offers page, so the sales rank is read too: "
                        "every reading lands in the product tool's bsr_points_hot, and its "
                        "offers page in buybox_price_points_hot as with offers. A "
                        "product-page read draws 2 snapshots of the allowance (12h = 4 a "
                        "day). Like interval, every call sets it: tracking the same ASIN "
                        "again without read switches it back to offers."
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
            "interval, read (offers or product_page), expiry, whether the hot lane has picked "
            "it up, the lane's last and next read, plus the plan's tracking allowance "
            "(snapshots a day: total, used, remaining). USE WHEN the user asks what is being "
            "tracked, whether a tracking is live, how much allowance is left, or wants to "
            "stop one (the id goes to DELETE /v1/track/{id} on the REST API). Stopped "
            "trackings stay listed for 30 days. COST 0 credits. Paid plans only."
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
                "asin": {
                    "type": "string",
                    "description": (
                        "Only these products: one ASIN or up to 500 comma-separated "
                        "(2026-10-30)."
                    ),
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
            "the account's batches; action=schedule repeats a batch every 12 hours / daily / "
            "weekly / monthly (credit_ceiling, webhook_url); action=delete removes a batch. "
            "USE WHEN the user has more than a handful of ASINs, barcodes, search terms, "
            "seller ids, brands or seeds to run, wants a daily/weekly refresh, or wants a "
            "CSV. Kinds: product (asins or gtins - or source=tracked for the ASINs this "
            "account tracks, typically with include [history_only] at 0.05 a row), search "
            "(terms, live SERP), seller / brand / category / keywords (paid plans), and every "
            "other endpoint as its own kind (shopping, warehouse_search, bestsellers, offers, "
            "deals, seller_products, seller_brands, seller_network, brand_sellers, "
            "brand_network, keywords_compare, categories, category_search, brands_top, "
            "brands_movers, sellers_top, sellers_movers, categories_top) with the endpoint's "
            "query parameters in params. Each row bills what the endpoint bills; failed, "
            "not-found and duplicate rows are never billed; runs are serialized per "
            "marketplace. COST estimate / status / results / list are free; create + run "
            "queue billable rows (the estimate is the ceiling). API key required (keyed "
            "lanes)."
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
                        "product batches: tracked = the ASINs this account tracks on the "
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
                    "description": (
                        "category / categories batches (ids, or root); deals batches (deals "
                        "department ids, or all for the whole deals page)."
                    ),
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
                    "enum": ["none", "12h", "daily", "weekly", "monthly"],
                    "description": (
                        "schedule: how often the batch re-runs (none stops the schedule). 12h "
                        "fires twice a day, at at_hour_utc and 12 hours later; daily once a "
                        "day at at_hour_utc (default midnight UTC); weekly on Monday and "
                        "monthly on the 1st, 00:00 UTC."
                    ),
                },
                "at_hour_utc": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 23,
                    "description": (
                        "schedule, 12h and daily only: the UTC hour it fires at (12h: this "
                        "hour and 12 hours later). Default: 12h = the current UTC hour, daily "
                        "= 0. Kept when the same cadence is saved again without it."
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
            "ACCOUNT: the account's balance, plan, 30-day usage by endpoint and its "
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
    "connector. Free, no signup: 5 shopping searches/day. Unlimited use, full history and "
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
