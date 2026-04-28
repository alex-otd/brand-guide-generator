# brandgen Architecture Specification

This is the source of truth for what brandgen is, how it's built, and the rules anyone implementing it must follow. It is written to be self-contained: any developer (human or LLM) should be able to implement any module in this project armed with only this document, the scaffold code, and `BUILD_ORDER.md`.

---

## Table of Contents

1. [How to Use This Document](#1-how-to-use-this-document)
2. [Project Goal](#2-project-goal)
3. [Non-Negotiable Principles](#3-non-negotiable-principles)
4. [Tech Stack](#4-tech-stack)
5. [Coding Standards](#5-coding-standards)
6. [Architecture Overview](#6-architecture-overview)
7. [Data Models (Pipeline Contracts)](#7-data-models-pipeline-contracts)
8. [Module Specifications](#8-module-specifications)
9. [Validation Strategy](#9-validation-strategy)
10. [When to Stop and Ask the Architect](#10-when-to-stop-and-ask-the-architect)
11. [Common Pitfalls](#11-common-pitfalls)
12. [Reference: Gemini Session Kickoff Prompt](#12-reference-gemini-session-kickoff-prompt)

---

## 1. How to Use This Document

### If you are the human owner

This document is your project bible. Start a new Gemini session with the kickoff prompt in section 12, paste this document and `BUILD_ORDER.md` into the context, then point at the next unchecked item in `BUILD_ORDER.md`. When Gemini finishes, you run the validation gate. If it passes, check the box and move on. If it fails or Gemini hits a "stop and ask" trigger, bring the question back to Claude.

### If you are an LLM (Gemini, Claude, etc.) implementing a module

Read sections 1–7 in full before writing any code. They are short. Then jump to the specific module specification in section 8.

You are not the architect. Your job is to implement the module specified, following the principles and standards exactly. If anything is ambiguous, **stop and ask** rather than guess. See section 10.

---

## 2. Project Goal

**brandgen** is a CLI tool that scrapes websites and produces visual brand style guides for designers and developers.

### Inputs
- A single URL
- A CSV of URLs (with a `url` column)
- An XML sitemap URL (sitemap-index files recursively expanded)

### Outputs (per client, in `brand-guides/<client-slug>/`)
- `site/` — offline-viewable HTML/CSS/asset archive of every scraped page
- `brand.json` — machine-readable extracted brand data
- `branding-doc.html` — print-ready brand style guide (designed to be printed to PDF and sent to a developer)
- `config.yaml` — per-client configuration, auto-generated on first run, hand-editable

### Use case
A digital agency takes on a new client with no formal brand guide. Instead of a designer manually inspecting the live site to pull colors, fonts, button styles, etc. for a new landing page, the agency runs `brandgen all <client-url>` and gets a complete style guide in minutes. The output can be uploaded to an LLM along with new design work to verify alignment.

### Scope (v1, proof-of-concept)
- In: visual style extraction (colors, fonts, buttons, logo, contrast)
- In: post-JavaScript rendering (sites built with React, Vue, Divi, etc.)
- In: up to 10 pages per site
- Out: brand voice / tone / messaging (left as a fillable section for human/LLM authoring)
- Out: authenticated pages, e-commerce variants, video extraction
- Out: mobile breakpoint capture (deferred to v2)

---

## 3. Non-Negotiable Principles

These are the project owner's stated principles. Every implementation choice must align with them. **An implementation that violates these is wrong even if it works.**

### The 6Ps
**P**roper **P**lanning **P**revents **P**iss **P**oor **P**erformance.

### The Six Rules

1. **No black boxes.** Every step must be inspectable and explainable. If a function makes a non-obvious decision, the decision logic must be readable in plain Python with comments. Library calls that hide important logic are flagged for evaluation.
2. **Zero vendor lock-in.** Open-source dependencies only. No paid APIs. No proprietary formats. The output must be readable without our tool present.
3. **Systems should scale.** Write code that supports the next 100 client runs, not just the first. No hardcoded values that should be config. No assumptions about specific sites.
4. **No hacks, just real foundations.** Solving a problem with a quick string replace where a parser is needed is forbidden. If something's broken, fix the root cause.
5. **Fix the root, not the symptoms.** When a test fails, do not adjust the test to pass. When an extraction misses a value, do not add a hardcoded fallback. Find why the upstream data is wrong and fix that.
6. **Problem-solution breakdowns.** Every implementation decision should be traceable from the problem it solves to the solution chosen.

### Implications for Implementation

- Use direct, well-known libraries. Prefer `tinycss2` (small, transparent CSS tokenizer) over `cssutils` (larger, more magic). Prefer reading the WCAG formula and implementing it directly over importing `wcag-contrast-ratio` (one-liner formulas don't justify a dependency).
- Comment the **why**, not just the **what**. A line that does `r = (r + 0.055) / 1.055` is obvious; a comment saying "WCAG sRGB linearization step" is the value.
- Avoid clever Python. Readable code beats compact code every time.
- No "TODO: handle this case" without an issue tracking it. Either handle it or raise `NotImplementedError` with a clear message.

---

## 4. Tech Stack

### Approved runtime dependencies

| Library | Version | Purpose |
|---|---|---|
| `click` | >=8.1 | CLI framework |
| `playwright` | >=1.40 | JavaScript-aware page rendering |
| `beautifulsoup4` | >=4.12 | HTML parsing |
| `tinycss2` | >=1.2 | CSS tokenization and parsing |
| `pydantic` | >=2.5 | Typed data models |
| `jinja2` | >=3.1 | HTML template rendering |
| `pyyaml` | >=6.0 | Per-client config files |
| `httpx` | >=0.25 | HTTP fetching for sitemap/CSV |
| `lxml` | >=4.9 | XML sitemap parsing |

### Approved dev dependencies

| Library | Purpose |
|---|---|
| `pytest` | Testing |
| `pytest-asyncio` | Async test support (Playwright is async) |
| `ruff` | Linting and formatting |

### Rules for dependencies

- **Do not add a new dependency without architect approval.** This includes seemingly obvious additions like `requests`, `numpy`, `pandas`, or `Pillow`. Each one is a vendor surface we have to maintain.
- If a function from the standard library can do the job, use the standard library. Examples: `urllib.parse` for URL handling, `csv` for CSV reading (we do already use httpx for fetching the CSV from a URL, but parsing is stdlib).
- If you genuinely need a new dependency, stop and ask. Include in the request: what it solves, what alternatives you considered, why the stdlib can't do it.

---

## 5. Coding Standards

### Style
- Python 3.11+ syntax. Use modern type hints (`list[str]` not `List[str]`, `X | None` not `Optional[X]`).
- 100-character line length (enforced by ruff config in `pyproject.toml`).
- All public functions and classes have docstrings. Format: brief one-liner, blank line, longer description if needed.
- All public functions have type hints on parameters and return values.
- No emojis anywhere — code, comments, output, docs.

### Comments
Comments explain **why**. The code already says **what**. Examples:

Bad:
```python
# Loop over colors
for color in colors:
```

Good:
```python
# Bucket near-duplicates: humans perceive #325a2b and #325a2c as the same
# color, so we collapse them into a single entry weighted by combined frequency.
for color in colors:
```

### Validation in every implementation

The owner's preference is that **every code change includes a validation step**. For Gemini sessions implementing a module:

1. Implement the module
2. Write or un-skip the corresponding tests in `tests/`
3. Run `pytest tests/test_<module>.py -v` and confirm green
4. If the module is not pure (it has I/O), run a manual smoke test as described in the validation gate for that phase

A module is not "done" until its validation gate passes.

### Error handling

- Fail loudly. `raise` early, with descriptive messages.
- Never silently swallow exceptions with `except: pass`.
- Use `NotImplementedError` for scaffolded functions, never `pass` or returning a fake value.
- For user-facing CLI errors, format them clearly. `click.ClickException` is the right vehicle.

### Documentation

- Module docstrings explain the module's role in the pipeline.
- Function docstrings describe inputs, outputs, side effects, and any non-obvious algorithm choices.
- A new module without docstrings is incomplete.
- The principle: "the next person to maintain this should not need to read our chat history."

### Tone of any output the tool prints

- No exclamation points.
- No "Great!" or "Done!" or "Successfully ...!".
- Plain status: `wrote 39 files`, `validation failed: 2 tests did not pass`, `scraping https://example.com (page 1 of 3)`.
- Errors include the file path and line where appropriate.

---

## 6. Architecture Overview

### Data flow

```
INPUT (URL / CSV / sitemap)
        |
        v
[crawler/input_parser]   detect input type, return URL list
        |
        v
[crawler/page_selector]  score, rank, cap at max_pages
        |
        v
[scraper/playwright_runner]  for each URL: render + capture
        |
        +--> [scraper/style_capture]    computed styles per element
        |
        +--> [scraper/hover_capture]    static + JS hover states
        |
        v
[archiver/asset_downloader]  download every referenced asset
        |
        v
[archiver/url_rewriter]      rewrite to relative local paths
        |
        v
PER-PAGE CAPTURE (saved to disk as JSON + HTML + assets)
        |
        v
[extractors/colors]    } each runs over all per-page captures
[extractors/fonts]     } and produces typed Pydantic models
[extractors/buttons]   }
[extractors/logo]      }
[extractors/contrast]  }
        |
        v
[aggregator/merger]    deduplicate + score across pages -> BrandProfile
        |
        v
[renderer/doc_builder] render Jinja2 template + write brand.json
        |
        v
OUTPUT (brand-guides/<slug>/{site/, brand.json, branding-doc.html})
```

### Module boundaries

Each module owns one stage. Modules communicate through Pydantic models, not raw dicts. This is the "no black boxes" principle in practice — every cross-module call has a typed contract.

- **Crawler** (`brandgen/crawler/`) — turns input into a final list of URLs to scrape.
- **Scraper** (`brandgen/scraper/`) — turns a URL into a page capture (HTML + computed styles + asset list).
- **Archiver** (`brandgen/archiver/`) — turns a page capture into a locally-viewable archive on disk.
- **Extractors** (`brandgen/extractors/`) — turn page captures into typed brand data pieces.
- **Aggregator** (`brandgen/aggregator/`) — merges per-page extractor output into one site-wide BrandProfile.
- **Renderer** (`brandgen/renderer/`) — turns a BrandProfile into the final HTML doc and JSON.
- **Config** (`brandgen/config.py`) — Pydantic models for per-client configuration.
- **CLI** (`brandgen/cli.py`) — wiring only. No business logic.

### Folder layout (final, after all phases complete)

```
/main-dev/
├── brandgen/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── input_parser.py
│   │   └── page_selector.py
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── playwright_runner.py
│   │   ├── style_capture.py
│   │   └── hover_capture.py
│   ├── archiver/
│   │   ├── __init__.py
│   │   ├── asset_downloader.py
│   │   └── url_rewriter.py
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── colors.py
│   │   ├── fonts.py
│   │   ├── buttons.py
│   │   ├── logo.py
│   │   └── contrast.py
│   ├── aggregator/
│   │   ├── __init__.py
│   │   └── merger.py
│   └── renderer/
│       ├── __init__.py
│       ├── doc_builder.py
│       └── templates/
│           └── brand_doc.html.j2
├── tests/
│   ├── conftest.py
│   ├── fixtures/
│   └── test_*.py
├── brand-guides/
│   └── <client-slug>/
│       ├── config.yaml
│       ├── captures/         (raw scraper output, JSON)
│       ├── site/
│       │   ├── _shared/css/
│       │   ├── homepage/
│       │   ├── about/
│       │   └── ...
│       ├── brand.json
│       └── branding-doc.html
├── pyproject.toml
├── README.md
├── BUILD_ORDER.md            this build checklist
├── ARCHITECTURE.md           this document
├── setup_scaffold.py
├── .gitignore
└── .python-version
```

---

## 7. Data Models (Pipeline Contracts)

These Pydantic models define what each stage produces. They live in the modules listed below, and are imported across the codebase. They are the canonical interfaces — no raw dicts cross module boundaries.

The skeleton models exist in the scaffold. Implementations may add fields as needed but must not remove fields without architect approval (downstream code depends on them).

### `ClientConfig` — `brandgen/config.py`
Loaded from `brand-guides/<slug>/config.yaml`. Fields documented inline in the scaffold.

### `PageCapture` (to be added in Phase 2)
The output of one Playwright page render. Should include:
- `url: str`
- `final_url: str` (after redirects)
- `title: str`
- `html: str` (post-JavaScript DOM)
- `inline_styles: list[str]` (contents of all `<style>` blocks)
- `linked_stylesheets: list[str]` (URLs of all `<link rel="stylesheet">`)
- `element_styles: list[ElementStyle]` (sample of computed styles)
- `asset_urls: list[str]` (every URL the page referenced)
- `screenshot_path: Path | None`

### `ElementStyle` (to be added in Phase 2)
- `selector: str` (which sample selector matched it)
- `tag: str`
- `classes: list[str]`
- `id: str | None`
- `text: str` (truncated)
- `bounding_box: dict` (`{x, y, width, height}` from Playwright)
- `styles: dict[str, str]` (computed style values)
- `hover_styles: dict[str, str] | None` (set by hover_capture, Phase 7)

### `ExtractedColor` — `brandgen/extractors/colors.py` (skeleton in scaffold)
### `ExtractedFont` — `brandgen/extractors/fonts.py` (skeleton in scaffold)
### `ExtractedButton` — `brandgen/extractors/buttons.py` (skeleton in scaffold)
### `LogoCandidate` — `brandgen/extractors/logo.py` (skeleton in scaffold)
### `ContrastResult` — `brandgen/extractors/contrast.py` (skeleton in scaffold)
### `BrandProfile` — `brandgen/aggregator/merger.py` (skeleton in scaffold)

When implementing these, refer to the scaffold for the field set and types. Add fields only when the spec for the implementation calls for them.

---

## 8. Module Specifications

Each module has a dedicated spec below. Implement strictly to the spec. If something is missing, see section 10.

### 8.1 `brandgen/extractors/contrast.py`

**Purpose:** Compute WCAG contrast ratios. Pure math, no I/O.

**Public interface (from scaffold):**
- `relative_luminance(rgb: tuple[int, int, int]) -> float`
- `contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float`
- `compute_contrast_matrix(colors: list[str], pairings: list[tuple[str, str]]) -> list[ContrastResult]`

**Algorithm:**

For `relative_luminance`: implement the WCAG formula directly. Steps:
1. Normalize each channel to [0, 1] by dividing by 255.
2. Apply sRGB linearization: if channel ≤ 0.03928, divide by 12.92; otherwise `((c + 0.055) / 1.055) ** 2.4`.
3. Return `0.2126 * R + 0.7152 * G + 0.0722 * B`.

For `contrast_ratio`: implement the WCAG formula directly:
- `(L_lighter + 0.05) / (L_darker + 0.05)`
- Where L_lighter = max of the two luminances.

For `compute_contrast_matrix`:
- Accept hex strings in `colors` (e.g. `"#325a2b"`) and `pairings` (list of `(foreground_hex, background_hex)` tuples).
- For each pairing, parse to RGB, compute ratio, populate `ContrastResult` flags per WCAG thresholds.
- WCAG thresholds:
  - AA normal text: ratio >= 4.5
  - AA large text: ratio >= 3.0
  - AAA normal text: ratio >= 7.0
  - AAA large text: ratio >= 4.5
  - WCAG 2.1 UI components: ratio >= 3.0
- "Large text" definition (per WCAG): >= 18pt regular OR >= 14pt bold. The caller is responsible for knowing whether their pairing is large text; this function reports both flags.

**Edge cases:**
- Hex strings may or may not include `#` prefix. Handle both. Lowercase the output.
- Hex strings may be 3-char shorthand (`#fff`). Expand to 6-char before parsing.
- Invalid hex (non-hex characters, wrong length): raise `ValueError` with the offending value in the message.

**Tests required (`tests/test_contrast.py`):**
- White (#ffffff) on black (#000000) returns ratio of exactly 21.0
- Black on white also returns 21.0 (order independent)
- Same color on itself returns 1.0
- Premier Remodel test cases: copper (#b85c38) on white (#ffffff) — should be approximately 4.13 (fails AA normal, passes AA large)
- 3-char shorthand: `#fff` parses identically to `#ffffff`
- Invalid hex raises `ValueError`
- Verify against WebAIM contrast checker for at least 3 known pairings

### 8.2 `brandgen/scraper/style_capture.py`

**Purpose:** Define what styles to capture from each rendered page, and the JS that runs inside the browser to do the capture.

**Public interface:**
- `ELEMENT_SAMPLE_SELECTORS: list[str]` (already in scaffold)
- `COMPUTED_STYLE_PROPERTIES: list[str]` (already in scaffold)
- `async def capture_element_styles(page) -> list[ElementStyle]`

**Algorithm:**

`capture_element_styles` runs JavaScript inside the page (via `page.evaluate(...)`) to:
1. For each selector in `ELEMENT_SAMPLE_SELECTORS`, query all matching elements (cap at 50 per selector to avoid runaway captures on long pages).
2. For each matched element, build a record:
   - `selector`: which sample selector matched
   - `tag`: element tag name (lowercase)
   - `classes`: array of class names
   - `id`: element id or null
   - `text`: `innerText` truncated to 100 chars
   - `bounding_box`: `getBoundingClientRect()` as plain object
   - `styles`: object of computed style values for each property in `COMPUTED_STYLE_PROPERTIES`
3. Return the list of records back to Python.

The JS payload should be a string sent to `page.evaluate`, not a separate JS file (keeps the module self-contained).

**Edge cases:**
- Elements with `display: none` or `visibility: hidden`: include them but flag with a `visible: false` field. They still indicate brand intent.
- Pseudo-elements (`::before`, `::after`): out of scope for v1. Document this in a TODO comment.
- Iframe contents: out of scope for v1. Same-origin iframes could be captured later but skip for now.

**Tests required (`tests/test_style_capture.py`, new file):**
- Pure-Python tests on the constants (no Playwright needed): confirm the lists are non-empty and contain the expected critical entries.
- Playwright-based integration test against a fixture HTML file (`tests/fixtures/style_capture_basic.html`). Skip if Playwright not installed locally.

### 8.3 `brandgen/scraper/playwright_runner.py`

**Purpose:** Orchestrate Playwright. Open a URL, wait for full render, run capture, save artifacts.

**Public interface:**
- `async def render_page(url: str, output_dir: Path, config: ClientConfig) -> PageCapture`

**Algorithm:**

1. Launch Chromium headlessly with default viewport 1440x900.
2. Set a realistic user agent. (Default Playwright UA gets blocked by Cloudflare on some sites.)
3. `page.goto(url, wait_until="networkidle")` with a 30-second timeout.
4. If navigation fails or returns a non-2xx status, raise a clear exception with the URL and status.
5. Optional: scroll to bottom of page in steps to trigger lazy-loaded content, then back to top. (Many sites only inject styles for elements as they enter the viewport.)
6. Capture:
   - Final URL after redirects (`page.url`)
   - Page title (`page.title()`)
   - Full HTML (`page.content()`)
   - Inline styles: query all `<style>` and collect their text content.
   - Linked stylesheets: query all `<link rel="stylesheet">` and collect their `href`.
   - Element styles via `style_capture.capture_element_styles(page)`.
   - Asset URLs: collect from `<img src>`, `<img srcset>`, `<source src>`, `<link rel="icon">`, `<video src>`, `<video poster>`, plus URLs found in inline styles via simple regex.
   - Full-page screenshot to `output_dir / "screenshot.png"`.
7. Save the `PageCapture` as JSON to `output_dir / "capture.json"`.
8. Return the `PageCapture` object.

**Edge cases:**
- Sites with cookie banners: leave them in place. They will be filtered out at extraction time via `config.ignore_selectors`.
- Sites that redirect to a country-specific domain: store both `url` and `final_url`.
- Sites with infinite scroll: the lazy-load step has a max-iterations cap (e.g. 10) to prevent infinite loops.
- Sites that block headless browsers: if detected (e.g. Cloudflare challenge page), raise a clear exception instructing the user to flag this site for manual handling. **Do not** attempt to bypass anti-bot measures — that would be a hack and a legal grey area.

**Tests required:**
- Smoke test against a known stable page (use `https://example.com` — small, reliable, won't change).
- Confirm the capture JSON contains expected fields and they're populated.

### 8.4 `brandgen/extractors/colors.py`

**Purpose:** From a list of `PageCapture` objects, return the top N brand colors.

**Public interface (from scaffold):**
- `extract_colors(captures: list[PageCapture], top_n: int = 8) -> list[ExtractedColor]`

**Algorithm:**

1. Collect every color value from:
   - `color`, `background-color`, `border-color` in element computed styles
   - All color tokens parsed out of inline styles and (later) external CSS
2. Normalize each color to canonical lowercase `#rrggbb`. Discard transparent and `rgba(*, 0)` values.
3. Weight each color by:
   - **Pixel area:** approximate by `bounding_box.width * bounding_box.height` of the element it appears on
   - **Role boost:** colors used on buttons, links, headings get a 1.5x multiplier (these are "intentional" brand uses); colors only on body text get 0.7x (often near-black, low signal).
4. Bucket near-duplicates within a small ΔE (color distance). Implement perceptual distance using the CIE Lab color space (use Lab via direct math from sRGB — see implementation note below).
5. Demote colors that are obviously body text or background-of-body (near pure white, near pure black, neutral grays). Do not remove them — they are informational. But push them down the ranking unless they have unusually high weight.
6. Tag each surviving color with the roles it played: `["button-bg", "heading", "link", "border", ...]`.
7. Compute a confidence score: rough heuristic combining frequency, role boost, and intentional-use signal (presence in CSS variables would be a strong signal — check `--*` declarations in stylesheets).
8. Return top N as `ExtractedColor` objects.

**Implementation note on Lab conversion:**
Do not add a dependency for color math. Implement sRGB → XYZ → Lab using the standard formulas. This is ~30 lines of code, well-documented online, and aligns with the no-black-boxes principle.

**Edge cases:**
- Sites using CSS custom properties (`--brand-color: #325a2b`) — these are gold. If detected in stylesheets, give those colors a confidence boost and surface them even if their weighted frequency is moderate.
- Colors expressed as `rgb()`, `rgba()`, `hsl()`, `hsla()`, named (`red`), or shorthand hex — all must normalize to `#rrggbb`.
- Sites with thousands of unique colors due to gradients or photos: cap input at 1000 unique values per page (top by area weight) to keep extraction fast.

**Tests required (`tests/test_colors.py`):**
- Fixture: a synthetic `PageCapture` with known styles. Confirm the top 3 colors match what the fixture set up.
- Near-duplicate bucketing: two colors `#325a2b` and `#325b2c` should merge.
- Body text demotion: `#000000` used only in `p` tags should not appear in top 3 if other colors are present.
- CSS custom properties detection: a fixture with `--primary: #325a2b` confirms confidence boost.

### 8.5 `brandgen/extractors/fonts.py`

**Purpose:** Extract every font family in active use, plus weights, sizes, line-heights.

**Public interface (from scaffold):**
- `extract_fonts(captures: list[PageCapture]) -> list[ExtractedFont]`

**Algorithm:**

1. For each `ElementStyle` across all captures, parse its `font-family` value into a fallback chain (split on `,`, strip quotes and whitespace).
2. Take the first family in each chain (the "intended" family).
3. Group all element styles by intended family. For each family, collect:
   - All `font-weight` values seen (normalize keywords to numeric: `normal`=400, `bold`=700)
   - All `font-size` values seen (convert to px; 1em ≈ 16px assumed for em conversion if no parent context — flag this in a comment as a known limitation)
   - All `line-height` values seen (numeric only; ignore `normal`)
4. Tag each family with the roles it plays (heading/body/button) by looking at which selectors used it.
5. Detect source by parsing `@font-face` rules in collected stylesheets, plus `<link>` tags pointing at `fonts.googleapis.com` etc. Map family names to sources.
6. Return list of `ExtractedFont` sorted by usage frequency (most-used first).

**Edge cases:**
- System font stacks (e.g. `-apple-system, BlinkMacSystemFont, ...`): preserve the full chain in `fallbacks`, set `family` to the first non-system family if any, or `"system-ui"` placeholder otherwise.
- Variable fonts: weight may be a non-standard value like 350. Preserve as-is; do not snap to 100/200/.../900.
- Multiple `@font-face` declarations for the same family (different weights): consolidate.

**Tests required (`tests/test_fonts.py`):**
- Fixture with `font-family: 'Open Sans', sans-serif` produces an `ExtractedFont` with family `"Open Sans"` and fallback `["sans-serif"]`.
- Multiple weights of the same family consolidate into one entry with `weights_used` listing all.
- Google Fonts link tag is detected and `source` is set correctly.

### 8.6 `brandgen/extractors/buttons.py`

**Purpose:** Identify all button variants on the site and rank them by prominence.

**Public interface (from scaffold):**
- `extract_buttons(captures: list[PageCapture]) -> list[ExtractedButton]`

**Algorithm:**

1. Across all captures, collect every element matching button-like selectors: `<button>`, `<input type=button|submit|reset>`, `<a>` with `.btn`/`.button` class or `role="button"`, anything with class containing the case-insensitive substring `button`.
2. For each candidate, build a "style fingerprint" tuple of normalized properties: `(background, color, border, border_radius, padding, font_family, font_size, font_weight, text_transform)`.
3. Cluster by exact fingerprint. Then merge clusters whose fingerprints differ only by visually-imperceptible amounts (e.g. background colors within a small ΔE).
4. For each cluster, populate an `ExtractedButton` with:
   - All fingerprint fields
   - `frequency`: count of elements in the cluster
   - `example_text`: the actual text from the most common button in the cluster
   - `label`: assigned by ranking — most prominent CTA = `"primary"`, next = `"secondary"`, etc. Prominence heuristic: combination of frequency, color contrast against page background, and presence in viewport-prominent positions (header, hero section).
   - Hover fields populated only if hover capture has been run (Phase 7).
5. Return list sorted by prominence (primary first).

**Edge cases:**
- Disabled-state buttons (`[disabled]`, opacity < 1): exclude from primary/secondary determination but include as their own variant in the output.
- Site with hundreds of links styled as buttons (e.g. a gallery): cap at 200 candidates per page.
- Inline-styled overrides: if computed style differs from class-based style, computed wins (it's what users see).

**Tests required (`tests/test_buttons.py`):**
- Two buttons with identical styling cluster into one entry with frequency 2.
- A high-contrast orange CTA among muted gray buttons gets labeled `"primary"`.
- Disabled button does not displace the primary CTA.

### 8.7 `brandgen/extractors/logo.py`

**Purpose:** Best-effort logo identification with a confidence score. Always flagged for human verification.

**Public interface (from scaffold):**
- `extract_logo_candidates(captures: list[PageCapture]) -> list[LogoCandidate]`

**Algorithm:**

For each capture (homepage prioritized), score every `<img>` and `<svg>` by:

1. **Location score:** Inside `<header>` or `<nav>`: +50. In top 200px of page: +30. Top-left quadrant: +20. In `<footer>`: +15.
2. **Naming score:** `alt`, `src`, `class`, or `id` contains "logo": +40. Contains the client domain name root: +20.
3. **Format score:** SVG: +15 (logos are commonly SVG). PNG with transparency: +10. Reasonable aspect ratio (between 1:1 and 5:1): +5.
4. **Anti-signals:** Inside an article body, hero section background image, decorative pattern: -30.

Sort candidates by total score, return top 5. Set `confidence` to `min(score / 100, 1.0)` for each.

**Edge cases:**
- Site with an SVG logo inlined directly in the header: capture the `<svg>` outerHTML as `src` (data URI form).
- Site that uses background-image in CSS for the logo: parse CSS for `header *` background images and include as candidates.
- Multiple logos (header + footer): both surface as candidates, header version scores higher.

**Tests required (`tests/test_logo.py`):**
- Fixture HTML with an `<img alt="Premier Remodel logo">` in `<header>` ranks as the top candidate.
- Fixture with a hero background image and a header logo still ranks the header logo first.

### 8.8 `brandgen/aggregator/merger.py`

**Purpose:** Merge per-page extractor outputs into one site-wide `BrandProfile`.

**Public interface:**
- `def merge_extractions(per_page: list[dict], client_slug: str) -> BrandProfile`

Where each dict in `per_page` is `{"colors": [...], "fonts": [...], "buttons": [...], "logo_candidates": [...]}` from running every extractor over one capture.

**Algorithm (Phase 4 single-page version):**
- Take the first (and only) per-page entry.
- Compute the contrast matrix from the colors found (use `compute_contrast_matrix` from `extractors.contrast`).
- Wrap into a `BrandProfile`.

**Algorithm (Phase 5 multi-page extension):**
- Colors: bucket by Lab distance, sum frequencies, union roles, recompute confidence.
- Fonts: union by family, union weights/sizes per family, recompute roles.
- Buttons: re-cluster across pages — a primary CTA on page 1 and page 5 should be the same entry.
- Logos: pick top candidate by confidence across all pages (homepage entries weighted higher).
- Contrast: recompute from the merged color list.

**Tests required (`tests/test_merger.py`):**
- Single-page merge passes through unchanged.
- Multi-page merge: identical button on two pages collapses to one entry with frequency = sum.
- Color appearing on multiple pages has summed frequency and unioned roles.

### 8.9 `brandgen/renderer/doc_builder.py` and `brand_doc.html.j2`

**Purpose:** Render the final HTML brand doc and the `brand.json` sidecar from a `BrandProfile`.

**Public interface (from scaffold):**
- `render_brand_doc(profile: BrandProfile, output_dir: Path) -> Path`
- `write_brand_json(profile: BrandProfile, output_dir: Path) -> Path`

**Template requirements (`brand_doc.html.j2`):**

The output mirrors the Premier Remodel reference doc supplied by the project owner. Key sections, in order:

1. **Header:** Client display name, "Brand Style Guide" title.
2. **Brand Voice & Identity:** **Empty placeholder section** with a comment explaining it should be filled in via LLM upload + human review. Do not auto-generate this section.
3. **Color Palette:** Grid of swatches. Each swatch shows the color, a name (or just the hex), the hex code, and a one-line role description. 5-8 swatches typical.
4. **Typography:** For each `ExtractedFont`, show real samples in that font with the weights and sizes observed. Include H1/H2/H3 examples plus body text.
5. **Buttons:** Each `ExtractedButton` rendered as an actual button, both resting and (when available, Phase 7+) hover state. Style notes below each.
6. **WCAG Contrast:** Table of color pairings with their ratios and pass/fail flags for AA normal, AA large, AAA. Highlight any pairings used in the wild that fail their context.
7. **Logo:** Top logo candidate displayed, with a "human verification required" note. Lower-confidence alternatives listed below.

**Print-readiness rules (CSS):**
- Use `@media print` to set page margins.
- Use `break-inside: avoid` on each color swatch, button example, and section block.
- Use `print-color-adjust: exact; -webkit-print-color-adjust: exact;` so swatches actually print in color.
- Page-break before each major section (color, typography, buttons, etc.) so a printed PDF has clean section starts.

**brand.json shape:**
- Top level: `{"client_slug", "generated_at", "source_pages", "brand_profile"}`.
- `brand_profile` contains everything in `BrandProfile` serialized via `model_dump_json(indent=2)`.
- Goal: an LLM can read this and answer questions about the brand without parsing HTML.

**Tests required (`tests/test_doc_builder.py`):**
- A fixture `BrandProfile` produces an HTML file containing all expected section headings.
- The output HTML passes basic structure checks (valid HTML5, contains expected swatches).
- `brand.json` round-trips: load it, parse to `BrandProfile`, all data preserved.

### 8.10 `brandgen/cli.py`

**Purpose:** Wire up Click commands. **No business logic in this file.** All work is delegated to the appropriate subpackage.

The scaffold has `scrape`, `extract`, `render`, and `all` already declared. Implementation only needs to fill in the bodies, which should be ~5-15 lines each calling into the right modules.

The `all` command runs `scrape -> extract -> render` in sequence, printing progress between each phase.

### 8.11 Crawler modules — `brandgen/crawler/`

`input_parser.py`:
- `parse_input(input_source: str) -> list[str]` — dispatch based on suffix and content type.
- `parse_csv(path: Path) -> list[str]` — use the standard library `csv` module. Expect a `url` column header; raise `ValueError` if missing.
- `parse_sitemap(url: str) -> list[str]` — fetch via `httpx`, parse via `lxml`. Recurse into `<sitemapindex>` entries up to 2 levels deep.

`page_selector.py`:
- `select_pages(candidate_urls: list[str], config: ClientConfig) -> list[str]`
- Score each URL by:
  - First-pattern-match score from `config.priority_patterns` (highest match wins)
  - URL depth penalty: `-5 per path segment`
  - Position-in-source bonus: `+1 per spot above position 100` (capped)
- Forced paths (`config.forced_paths`) bypass scoring and are always included.
- Homepage is always included if it appears in candidates.
- Cap at `config.max_pages`.

### 8.12 Archiver modules — `brandgen/archiver/`

`asset_downloader.py`:
- `download_assets(asset_urls: list[str], output_dir: Path) -> dict[str, Path]`
- Use `httpx` async with a concurrency limit (default 8).
- Skip `data:` URIs and obvious tracking pixels (matched by domain regex).
- Save to `output_dir` preserving filename; if collision, suffix with hash of URL.
- Return mapping of original URL to local file path.

`url_rewriter.py`:
- `rewrite_html_urls(html_path: Path, asset_map: dict[str, Path]) -> None` — use BeautifulSoup, modify in place.
- `rewrite_css_urls(css_path: Path, asset_map: dict[str, Path]) -> None` — use tinycss2 to tokenize, replace `url(...)` tokens.
- Both should emit a comment at the top: `<!-- Rewritten by brandgen for offline viewing on YYYY-MM-DD -->`.

### 8.13 Hover capture — `brandgen/scraper/hover_capture.py` (Phase 7)

Implementation deferred to Phase 7. Specification will be added then; for now the scaffold stub is sufficient.

### 8.14 Config — `brandgen/config.py` (Phase 8)

Implementation of `load_client_config` and `write_default_client_config` deferred to Phase 8. The Pydantic model `ClientConfig` is already defined in the scaffold.

---

## 9. Validation Strategy

### Three layers of testing

1. **Unit tests** — pure functions with no I/O, fixture-based. Fast. Should always be green.
2. **Integration tests** — modules that touch the file system or run Playwright. Slower; may be tagged for selective runs.
3. **End-to-end manual validation** — run the full CLI against the three test sites (Premier Remodel, One Thing Digital, Rakks) and inspect output.

### What "validated" means before checking a box in BUILD_ORDER.md

For each module:
- All listed tests pass under `pytest`
- The validation gate for the phase passes (run the manual check described in BUILD_ORDER.md)
- No new linting errors introduced (`ruff check brandgen/`)

### Test fixtures location

- Synthetic HTML/CSS fixtures: `tests/fixtures/<module>/<test_name>.html`
- Synthetic captured-data fixtures: `tests/fixtures/<module>/<test_name>.json`
- Real-site reference captures (for regression): `tests/fixtures/sites/<slug>/<page>.json`

---

## 10. When to Stop and Ask the Architect

If you are an LLM implementing a module, **stop and write a question** rather than guess in any of these situations:

1. **A new dependency is needed.** Approval required. Include alternatives considered.
2. **The spec is ambiguous or contradicts another section.** Quote both passages.
3. **A test is failing for reasons that require an architectural decision** (e.g. "the algorithm in section 8 says X but this real-world site requires Y").
4. **You catch yourself wanting to add a "TODO: handle this later" comment.** Either handle it now or stop and ask whether to handle it.
5. **You catch yourself wanting to write `except: pass` or a hardcoded fallback.** Stop. Ask.
6. **Performance is a problem and the answer would change architecture** (e.g. "this is too slow without caching, but caching changes module boundaries").
7. **A principle in section 3 seems to conflict with the cleanest implementation.** The principle wins; surface the conflict for awareness.
8. **You finish a module and the validation gate fails.** Diagnose, but do not modify the gate or the spec to make it pass.

Format for raising a question:

```
ARCHITECT_QUESTION
Module: brandgen/extractors/foo.py
Section reference: 8.X
Question: <one or two sentences>
Context: <what you tried, what you'd propose, why you're uncertain>
```

---

## 11. Common Pitfalls

These are mistakes likely to show up. Avoid them.

- **Adding pandas, numpy, requests, or Pillow.** Each is a useful library, none is needed. The standard library handles CSV; httpx handles HTTP; tinycss2 and BeautifulSoup handle parsing; we don't process pixel images.
- **Importing a color library for Lab conversion.** ~30 lines of math; we implement it ourselves.
- **Using regex to parse HTML.** Use BeautifulSoup. Always.
- **Using regex to parse CSS.** Use tinycss2. Almost always.
- **Catching exceptions to "make tests pass."** This is the symptom of a deeper problem. Find the cause.
- **Adding a `try/except` around an unfamiliar call "just in case."** If you don't know what can fail and how to handle it, don't catch.
- **Returning empty lists or `None` from functions to indicate failure.** Raise instead.
- **Hardcoding values that vary per site.** Move to `ClientConfig` or `DEFAULT_PRIORITY_PATTERNS`.
- **Writing comments that describe what the code does instead of why.** See coding standards.
- **Using emojis.** Anywhere.
- **Adding "successfully" or "" to log messages.** Plain status only.
- **Bypassing anti-bot measures.** This is out of scope and a legal grey area. If a site blocks the scraper, raise a clear exception; do not implement workarounds.
- **Modifying the scaffold's Pydantic models without architect approval.** You can add fields if the spec calls for them. Do not remove or rename existing fields.
- **Skipping the validation step.** Every module ships with its tests run and passing.

---

## 12. Reference: Gemini Session Kickoff Prompt

Use this as the first message in any Gemini session. Paste this document and `BUILD_ORDER.md` as attachments or in the context.

> You are implementing one module at a time for a Python project called brandgen. The full architectural specification is in the attached `ARCHITECTURE.md`. The build order and validation gates are in the attached `BUILD_ORDER.md`.
>
> Read `ARCHITECTURE.md` sections 1–7, plus the section in 8 that corresponds to the module I'm asking you to build. Also read sections 10 and 11 — those are non-negotiable.
>
> The next module to build is: **[paste module path here]**
>
> Rules:
>
> - Follow the principles in section 3 strictly.
> - Use only the dependencies listed in section 4.
> - Match the coding standards in section 5 — type hints, docstrings, no emojis, validation in every change.
> - When the spec is ambiguous, stop and ask using the format in section 10.
> - When you finish, output the implementation plus the test file. Then list the exact commands I should run to validate.
>
> Do not summarize what you're about to do. Do not add introductions or sign-offs. Output the code.

---

## Appendix A: Reference Output

The project owner supplied a reference brand guide for "Premier Remodel" as the target output format. That HTML file is the visual benchmark for what `branding-doc.html` should look like at the end of Milestone 1. Key structural elements:

- Color palette grid with swatches and hex codes
- Typography section with live samples
- Button examples in normal and hover states
- ADA/WCAG section with explicit contrast notes
- Print-ready styling (page-break rules, color-adjust: exact)

Variation from the reference is fine where the source site demands it — every client's data is different. But the structural layout and section ordering should match.

---

## Appendix B: Three Test Sites

Validation across these three sites is required before any milestone is considered complete:

1. **Premier Remodel** — has a reference brand guide, known-good baseline
2. **One Thing Digital** — different industry, different platform
3. **Rakks** — different again, surfaces different edge cases

If a feature works on one but breaks on another, the feature isn't done.

---

*End of architecture specification.*
