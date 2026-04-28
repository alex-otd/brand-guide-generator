#!/usr/bin/env python3
"""
brandgen scaffold generator
============================
Creates the initial project structure for the brandgen tool inside a target
directory (default: current working directory).

Usage
-----
    python setup_scaffold.py                # creates structure in current dir
    python setup_scaffold.py /path/to/dir   # creates in a specific dir

After running this script, complete setup with:
    cd <target-dir>
    python -m venv .venv
    source .venv/bin/activate          # on Windows: .venv\\Scripts\\activate
    pip install -e ".[dev]"
    playwright install chromium

Design notes
------------
- Uses only the Python standard library so it can run on any Python 3.8+
  install without dependencies.
- Self-validating: after creating files, it verifies every expected path
  exists and attempts a sanity import of the brandgen package.
- Idempotent: running twice will skip existing files (will not overwrite).
  Pass --force to overwrite.

Long-term ownership
-------------------
This script is intentionally self-contained: all stub file contents live in
one dictionary at the top of the file. To add a new module to the project
skeleton, add an entry to the FILES dict and re-run. Nothing else changes.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from textwrap import dedent

# ---------------------------------------------------------------------------
# Configuration: every file the scaffold will create.
#
# Keys are paths relative to the target directory. Values are the file
# contents as strings. Empty strings are valid (used for __init__.py and
# .gitkeep markers).
#
# Stubs follow this convention:
#   - Module docstring describing purpose and what will live here
#   - Imports needed for type hints
#   - Function/class signatures with NotImplementedError or pydantic BaseModel
#   - A short "Implementation roadmap" comment listing what must be built
#
# This way every stub doubles as a spec for the file we will write next.
# ---------------------------------------------------------------------------

# Marker constant used in many stubs to indicate unimplemented behavior.
# Defined once so we can grep for it later to find unfinished work.
TODO_MARKER = "TODO(brandgen): implement"


def _stub(purpose: str, body: str) -> str:
    """Helper to assemble a consistent stub module.

    Parameters
    ----------
    purpose : str
        One-line summary of what this module is for. Becomes the module
        docstring's first line.
    body : str
        The actual Python code body for the stub (function defs, class defs,
        etc). Will be appended after a standard header.

    Returns
    -------
    str
        Full file contents ready to write.
    """
    return dedent(f'''\
        """
        {purpose}

        Implementation status: stub. See {TODO_MARKER} markers below.
        """
        from __future__ import annotations

    ''') + body


FILES: dict[str, str] = {

    # =========================================================================
    # Project root configuration
    # =========================================================================

    "pyproject.toml": dedent('''\
        # Build configuration for brandgen.
        # Uses hatchling as the build backend: simple, PEP-517 compliant, no lock-in.

        [build-system]
        requires = ["hatchling"]
        build-backend = "hatchling.build"

        [project]
        name = "brandgen"
        version = "0.1.0"
        description = "Scrape websites and generate visual brand style guides for designers and developers"
        readme = "README.md"
        requires-python = ">=3.11"
        license = { text = "MIT" }
        authors = [{ name = "Your Name" }]
        keywords = ["branding", "scraper", "style-guide", "web-design"]
        classifiers = [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
        ]

        # Runtime dependencies. Lower bounds only — no upper pins so users
        # can pick up patch and minor updates without a release here.
        dependencies = [
            "click>=8.1",           # CLI framework
            "playwright>=1.40",     # JS-aware page rendering
            "beautifulsoup4>=4.12", # HTML parsing
            "tinycss2>=1.2",        # CSS tokenizer/parser
            "pydantic>=2.5",        # typed config and data models
            "jinja2>=3.1",          # HTML template rendering
            "pyyaml>=6.0",          # per-client config files
            "httpx>=0.25",          # sitemap and CSV fetching
            "lxml>=4.9",            # XML sitemap parsing
        ]

        # Development-only dependencies. Install with: pip install -e ".[dev]"
        [project.optional-dependencies]
        dev = [
            "pytest>=7.4",
            "pytest-asyncio>=0.23",
            "ruff>=0.1",
        ]

        # Registers the `brandgen` command-line entry point.
        # After `pip install -e .`, users can run `brandgen --help`.
        [project.scripts]
        brandgen = "brandgen.cli:cli"

        # Tells hatchling which directories to package.
        [tool.hatch.build.targets.wheel]
        packages = ["brandgen"]

        [tool.pytest.ini_options]
        testpaths = ["tests"]
        asyncio_mode = "auto"

        [tool.ruff]
        line-length = 100
        target-version = "py311"

        [tool.ruff.lint]
        select = ["E", "F", "I", "N", "UP", "B"]
    '''),

    "README.md": dedent('''\
        # brandgen

        Scrape websites and generate visual brand style guides for designers and developers.

        ## What it does

        Given a URL, a CSV of URLs, or an XML sitemap, brandgen will:

        1. Render up to 10 priority pages with a real browser (post-JavaScript)
        2. Save each page as an offline-viewable HTML archive
        3. Extract colors, fonts, buttons, logo candidates, and WCAG contrast ratios
        4. Produce a print-ready HTML brand style guide and a machine-readable `brand.json`

        Output lands in `brand-guides/<client-slug>/`.

        ## Installation

        ```bash
        # 1. Create a virtual environment
        python -m venv .venv
        source .venv/bin/activate    # Windows: .venv\\Scripts\\activate

        # 2. Install brandgen and its dev tools in editable mode
        pip install -e ".[dev]"

        # 3. Install the headless browser binary (one-time, ~300MB)
        playwright install chromium
        ```

        ## Quick start

        ```bash
        # Single URL
        brandgen scrape https://example.com --client-slug example

        # CSV of URLs
        brandgen scrape urls.csv --client-slug example

        # XML sitemap
        brandgen scrape https://example.com/sitemap.xml --client-slug example

        # End-to-end (scrape + extract + render in one command)
        brandgen all https://example.com --client-slug example
        ```

        ## Project structure

        ```
        brandgen/         source package
        tests/            unit tests
        brand-guides/     generated outputs (one folder per client)
        ```

        ## Status

        Proof-of-concept under active development. Stubs raise NotImplementedError
        until each module is built. Search the codebase for `TODO(brandgen)` to
        find unfinished work.

        ## Principles

        - No black boxes: every extraction step is inspectable and documented
        - No vendor lock-in: pure open-source dependencies
        - Fix the root, not symptoms: heuristics fail loudly with confidence scores
        - Cleanly commented for hand-off

        ## License

        MIT
    '''),

    ".gitignore": dedent('''\
        # Python
        __pycache__/
        *.py[cod]
        *$py.class
        *.so
        .Python
        build/
        dist/
        *.egg-info/
        .pytest_cache/
        .ruff_cache/

        # Virtual environments
        .venv/
        venv/
        env/

        # IDEs
        .vscode/
        .idea/
        *.swp

        # OS
        .DS_Store
        Thumbs.db

        # brandgen outputs
        # Per-client outputs may contain proprietary client material.
        # By default we ignore them; remove this line if you want to track them.
        brand-guides/*/
        !brand-guides/.gitkeep

        # Playwright traces and screenshots from debugging
        playwright-trace/
        test-results/
    '''),

    ".python-version": "3.11\n",

    # =========================================================================
    # brandgen package
    # =========================================================================

    "brandgen/__init__.py": dedent('''\
        """brandgen — scrape websites and generate visual brand style guides."""

        __version__ = "0.1.0"
    '''),

    "brandgen/cli.py": dedent('''\
        """
        Command-line interface for brandgen.

        Exposes the top-level `brandgen` command and its subcommands. Wiring
        only — actual work is delegated to the subpackages.

        Subcommands (all stubs at this stage):
          scrape    — fetch and archive pages from a URL/CSV/sitemap
          extract   — run the brand extractors over a previously-scraped client
          render    — generate the final HTML brand doc from extracted data
          all       — convenience wrapper running scrape -> extract -> render
        """
        from __future__ import annotations

        import click

        from brandgen import __version__


        @click.group()
        @click.version_option(__version__, prog_name="brandgen")
        def cli() -> None:
            """brandgen: scrape sites and generate brand style guides."""


        @cli.command()
        @click.argument("input_source")
        @click.option(
            "--client-slug",
            required=True,
            help="Short identifier for the client (used as the output folder name).",
        )
        @click.option(
            "--max-pages",
            default=10,
            show_default=True,
            help="Hard cap on number of pages to scrape.",
        )
        def scrape(input_source: str, client_slug: str, max_pages: int) -> None:
            """Scrape pages from INPUT_SOURCE (URL, CSV path, or sitemap URL)."""
            raise NotImplementedError(
                "TODO(brandgen): implement scrape command "
                "(see brandgen/scraper/playwright_runner.py)"
            )


        @cli.command()
        @click.option("--client-slug", required=True)
        def extract(client_slug: str) -> None:
            """Run brand extractors on an already-scraped client folder."""
            raise NotImplementedError(
                "TODO(brandgen): implement extract command "
                "(see brandgen/extractors/)"
            )


        @cli.command()
        @click.option("--client-slug", required=True)
        def render(client_slug: str) -> None:
            """Render the final HTML brand doc from extracted data."""
            raise NotImplementedError(
                "TODO(brandgen): implement render command "
                "(see brandgen/renderer/doc_builder.py)"
            )


        @cli.command(name="all")
        @click.argument("input_source")
        @click.option("--client-slug", required=True)
        def run_all(input_source: str, client_slug: str) -> None:
            """End-to-end: scrape, extract, and render in a single command."""
            raise NotImplementedError(
                "TODO(brandgen): wire up scrape -> extract -> render pipeline"
            )


        if __name__ == "__main__":
            cli()
    '''),

    "brandgen/config.py": dedent('''\
        """
        Pydantic models for brandgen configuration.

        Two layers of config:

        1. Tool defaults (hard-coded here) — sensible behavior out of the box.
        2. Per-client YAML at brand-guides/<slug>/config.yaml — overrides for
           tricky sites (custom priority paths, ignore selectors, manual color
           overrides).

        The per-client file is auto-generated on first scrape of a client and
        is hand-editable for re-runs.
        """
        from __future__ import annotations

        from pathlib import Path

        from pydantic import BaseModel, Field


        # Default page priority patterns (regex strings, case-insensitive).
        # Higher score = higher priority. Homepage always wins regardless.
        DEFAULT_PRIORITY_PATTERNS: dict[str, int] = {
            r"^/?$": 100,                                       # homepage
            r"^/(about|about-us)(/|$)": 80,
            r"^/(services?|what-we-do)(/|$)": 75,
            r"^/(contact|get-quote|quote)(/|$)": 70,
            r"^/(portfolio|gallery|projects|work)(/|$)": 60,
            r"^/(pricing|plans)(/|$)": 55,
            r"^/(team|staff)(/|$)": 50,
            r"^/(faq)(/|$)": 45,
            r"^/(blog|news)/.+": 40,                            # one blog post
        }


        class ClientConfig(BaseModel):
            """Per-client overrides loaded from brand-guides/<slug>/config.yaml."""

            client_slug: str = Field(..., description="Folder name under brand-guides/")
            display_name: str | None = Field(None, description="Human-readable name for the doc")

            # Page selection
            max_pages: int = 10
            priority_patterns: dict[str, int] = Field(default_factory=lambda: DEFAULT_PRIORITY_PATTERNS.copy())
            forced_paths: list[str] = Field(
                default_factory=list,
                description="Paths that must always be scraped, regardless of pattern matching.",
            )

            # Extraction tuning
            ignore_selectors: list[str] = Field(
                default_factory=list,
                description="CSS selectors to remove before extraction (e.g. '#cookie-banner').",
            )
            top_color_count: int = 8

            # Manual overrides for stubborn sites
            logo_url_hint: str | None = None
            primary_color_override: str | None = None


        def load_client_config(brand_guides_dir: Path, client_slug: str) -> ClientConfig:
            """Load (or create with defaults) the per-client config YAML."""
            raise NotImplementedError(
                "TODO(brandgen): implement YAML load with default-on-missing behavior"
            )


        def write_default_client_config(brand_guides_dir: Path, client_slug: str) -> Path:
            """Write a fresh default config.yaml for a new client, return the path."""
            raise NotImplementedError(
                "TODO(brandgen): implement default config writer"
            )
    '''),

    # ---------- crawler ----------
    "brandgen/crawler/__init__.py": "",

    "brandgen/crawler/input_parser.py": _stub(
        "Parse the three supported input forms (single URL, CSV, sitemap).",
        dedent('''\
            from pathlib import Path


            def parse_input(input_source: str) -> list[str]:
                """Detect input type and return a list of candidate URLs.

                Detection rules:
                - Ends in .csv (path or URL)        -> CSV
                - Ends in sitemap.xml or .xml       -> XML sitemap (recurse indexes)
                - Otherwise treated as a single URL -> wrap in a 1-element list

                The returned list is unfiltered. Page selection happens in
                page_selector.py.
                """
                raise NotImplementedError("TODO(brandgen): implement input dispatch")


            def parse_csv(path: Path) -> list[str]:
                """Read URLs from a CSV. Expects a `url` column header."""
                raise NotImplementedError("TODO(brandgen): implement CSV reader")


            def parse_sitemap(url: str) -> list[str]:
                """Fetch and parse an XML sitemap. Recurses sitemap-index files."""
                raise NotImplementedError("TODO(brandgen): implement sitemap fetcher")
        '''),
    ),

    "brandgen/crawler/page_selector.py": _stub(
        "Score and pick the top-N pages from a candidate URL list.",
        dedent('''\
            from brandgen.config import ClientConfig


            def select_pages(candidate_urls: list[str], config: ClientConfig) -> list[str]:
                """Apply priority scoring and return the top-N URLs to scrape.

                Scoring inputs:
                - Pattern match against config.priority_patterns
                - URL depth (shallower paths score higher)
                - Position in source list (earlier ranks higher as a tiebreaker)
                - Forced paths (config.forced_paths) bypass scoring

                Hard cap: config.max_pages. Homepage always included if present.
                """
                raise NotImplementedError("TODO(brandgen): implement priority scoring")
        '''),
    ),

    # ---------- scraper ----------
    "brandgen/scraper/__init__.py": "",

    "brandgen/scraper/playwright_runner.py": _stub(
        "Orchestrate Playwright to render a page and dump captures to disk.",
        dedent('''\
            from pathlib import Path


            async def render_page(url: str, output_dir: Path) -> dict:
                """Open `url` in headless Chromium, wait for network idle,
                then capture:

                - Post-JS HTML (full DOM after hydration)
                - Linked stylesheets (downloaded separately by archiver)
                - Inline <style> blocks
                - Computed styles for a structured element sample
                  (h1-h6, p, a, button, input, .btn, header, footer, ...)
                - Full-page screenshot (PNG, for visual diffing)
                - Asset manifest (every URL the page referenced)

                Returns a dict that downstream modules consume. Schema TBD.
                """
                raise NotImplementedError("TODO(brandgen): implement Playwright runner")
        '''),
    ),

    "brandgen/scraper/style_capture.py": _stub(
        "Compute and serialize CSS computed styles for an element sample.",
        dedent('''\
            ELEMENT_SAMPLE_SELECTORS: list[str] = [
                "h1", "h2", "h3", "h4", "h5", "h6",
                "p", "a", "button",
                "input", "textarea", "select",
                ".btn", ".button", "[role=button]",
                "header", "footer", "nav",
                "blockquote",
            ]
            # Properties we need to capture from window.getComputedStyle for each
            # sampled element. Keep narrow; computed styles dump enormous payloads
            # if you ask for everything.
            COMPUTED_STYLE_PROPERTIES: list[str] = [
                "color", "background-color", "background-image",
                "font-family", "font-size", "font-weight", "line-height",
                "letter-spacing", "text-transform",
                "border-color", "border-radius", "border-width", "border-style",
                "padding", "margin",
                "box-shadow", "text-shadow",
                "display",
            ]


            async def capture_element_styles(page) -> list[dict]:
                """Run getComputedStyle on each matching element. Returns list of
                {selector, tag, classes, id, text, styles: {prop: value}}.
                """
                raise NotImplementedError("TODO(brandgen): implement computed style capture")
        '''),
    ),

    "brandgen/scraper/hover_capture.py": _stub(
        "Capture button hover states via both static CSS rules and JS simulation.",
        dedent('''\
            async def capture_hover_deltas(page, button_selectors: list[str]) -> list[dict]:
                """For each button selector:

                1. Read computed styles in resting state
                2. page.hover() the element
                3. Re-read computed styles
                4. Diff and return only properties that changed

                This catches both CSS :hover rules (which would be visible in
                stylesheets anyway) AND JS-driven effects that only show up on
                actual hover events (React, Vue, jQuery handlers, Divi modules).
                """
                raise NotImplementedError("TODO(brandgen): implement hover delta capture")


            def parse_static_hover_rules(stylesheets: list[str]) -> list[dict]:
                """Parse CSS for :hover selectors and return the rules.

                A complement to capture_hover_deltas — together they give us
                a full picture of hover behavior on the page.
                """
                raise NotImplementedError("TODO(brandgen): implement :hover rule parser")
        '''),
    ),

    # ---------- archiver ----------
    "brandgen/archiver/__init__.py": "",

    "brandgen/archiver/asset_downloader.py": _stub(
        "Download every external asset a page references and save to disk.",
        dedent('''\
            from pathlib import Path


            def download_assets(asset_urls: list[str], output_dir: Path) -> dict[str, Path]:
                """Download each URL into output_dir, returning a {url: local_path} map.

                Handles:
                - CSS files (saved verbatim, will be rewritten by url_rewriter)
                - Web fonts (woff, woff2, ttf, otf)
                - Images (PNG, JPG, SVG, WebP) — including those referenced from CSS
                - Favicons

                Skips:
                - Tracking pixels (Google Analytics, Facebook, etc — configurable)
                - Analytics JS (we want post-JS DOM, not the JS itself)
                """
                raise NotImplementedError("TODO(brandgen): implement asset downloader")


            def deduplicate_shared_assets(site_dir: Path) -> None:
                """Move assets shared across pages into _shared/ folders.

                After scraping all pages, identical CSS files (by hash) get moved
                to site/_shared/css/ and per-page references are rewritten to
                point there. Keeps the archive smaller and easier to inspect.
                """
                raise NotImplementedError("TODO(brandgen): implement shared-asset dedup")
        '''),
    ),

    "brandgen/archiver/url_rewriter.py": _stub(
        "Rewrite absolute URLs in saved HTML/CSS to relative local paths.",
        dedent('''\
            from pathlib import Path


            def rewrite_html_urls(html_path: Path, asset_map: dict[str, Path]) -> None:
                """Update every src/href in saved HTML to point to local files.

                Operates on:
                - <link href> for stylesheets
                - <script src> for JS (kept disabled with a comment)
                - <img src> and <img srcset>
                - <source src> in <picture> / <video>
                - <a href> within the same domain (so internal navigation works
                  if the user opens the offline archive)
                """
                raise NotImplementedError("TODO(brandgen): implement HTML URL rewriting")


            def rewrite_css_urls(css_path: Path, asset_map: dict[str, Path]) -> None:
                """Update url() references inside CSS to relative local paths.

                Catches: background-image, @font-face src, list-style-image,
                cursor, mask-image, etc. Uses tinycss2 to tokenize so we don't
                trip over edge cases like comments-inside-strings.
                """
                raise NotImplementedError("TODO(brandgen): implement CSS URL rewriting")
        '''),
    ),

    # ---------- extractors ----------
    "brandgen/extractors/__init__.py": "",

    "brandgen/extractors/colors.py": _stub(
        "Extract a frequency- and role-weighted top-N color palette.",
        dedent('''\
            from pydantic import BaseModel


            class ExtractedColor(BaseModel):
                hex: str                    # canonical lowercase #rrggbb
                rgb: tuple[int, int, int]
                roles: list[str]            # e.g. ["body-text", "button-bg", "link"]
                frequency: float            # 0..1, weight of this color across the site
                confidence: float           # 0..1, how sure we are this is intentional brand


            def extract_colors(captures: list[dict], top_n: int = 8) -> list[ExtractedColor]:
                """Return the top N colors found across captured pages.

                Algorithm sketch (to be refined):
                1. Collect every color value from computed styles + parsed CSS.
                2. Weight by visible pixel area (approximated from element size).
                3. Bucket near-duplicates within a small Lab color distance.
                4. Tag each color with the roles it plays (text, bg, border, ...).
                5. Demote near-blacks/near-whites that are obviously body text/bg.
                6. Return top N with confidence scores.
                """
                raise NotImplementedError("TODO(brandgen): implement color extraction")
        '''),
    ),

    "brandgen/extractors/fonts.py": _stub(
        "Extract typography: families, weights, sizes, line-heights actually used.",
        dedent('''\
            from pydantic import BaseModel


            class ExtractedFont(BaseModel):
                family: str                       # canonical family name
                fallbacks: list[str]              # fallback chain as declared
                weights_used: list[int]           # e.g. [400, 500, 700]
                sizes_used: list[float]           # in px, sorted
                line_heights_used: list[float]
                roles: list[str]                  # ["heading", "body", "button"]
                source: str | None                # "Google Fonts", "self-hosted", "system"


            def extract_fonts(captures: list[dict]) -> list[ExtractedFont]:
                """Detect every font family in active use plus its weights/sizes.

                Pulls from two sources:
                - Computed styles on sampled elements (the canonical truth)
                - @font-face rules in collected stylesheets (for source detection)
                """
                raise NotImplementedError("TODO(brandgen): implement font extraction")
        '''),
    ),

    "brandgen/extractors/buttons.py": _stub(
        "Cluster buttons by visual style and identify primary vs secondary CTAs.",
        dedent('''\
            from pydantic import BaseModel


            class ExtractedButton(BaseModel):
                label: str                          # "primary", "secondary", "tertiary"
                background: str                     # hex
                color: str                          # hex
                border: str | None
                border_radius: str
                padding: str
                font_family: str
                font_size: float
                font_weight: int
                text_transform: str
                hover_background: str | None
                hover_color: str | None
                example_text: str                   # actual text from a real button
                frequency: int                      # how many times this style appears


            def extract_buttons(captures: list[dict]) -> list[ExtractedButton]:
                """Cluster every button-like element into visual variants.

                Includes <button>, <input type=button|submit>, anchors with
                .btn/.button classes, and elements with role="button".

                Clustering: hash each button on a tuple of normalized style
                properties; merge clusters within small visual distance.
                """
                raise NotImplementedError("TODO(brandgen): implement button clustering")
        '''),
    ),

    "brandgen/extractors/logo.py": _stub(
        "Best-effort logo identification (heuristic, flagged for human review).",
        dedent('''\
            from pydantic import BaseModel


            class LogoCandidate(BaseModel):
                src: str
                alt: str | None
                width: int | None
                height: int | None
                location: str             # "header", "footer", "nav", "other"
                confidence: float         # 0..1
                reason: str               # human-readable why-it-matched


            def extract_logo_candidates(captures: list[dict]) -> list[LogoCandidate]:
                """Return ranked logo candidates. Top item is the best guess.

                Heuristics (in priority order):
                1. <img>/<svg> inside <header> with 'logo' in alt/src/class/id
                2. First <img> in <header> by DOM order
                3. <img>/<svg> in top-left of viewport
                4. Branded-looking image referenced in <link rel="icon">

                We never auto-confirm a logo. The extracted doc shows the top
                candidate flagged for client confirmation.
                """
                raise NotImplementedError("TODO(brandgen): implement logo heuristics")
        '''),
    ),

    "brandgen/extractors/contrast.py": _stub(
        "Compute WCAG 2.0 AA and 2.1 contrast ratios for color pairings.",
        dedent('''\
            from pydantic import BaseModel


            class ContrastResult(BaseModel):
                foreground: str          # hex
                background: str          # hex
                ratio: float             # e.g. 4.52
                aa_normal_text: bool     # ratio >= 4.5
                aa_large_text: bool      # ratio >= 3.0
                aaa_normal_text: bool    # ratio >= 7.0
                aaa_large_text: bool     # ratio >= 4.5
                ui_components: bool      # ratio >= 3.0 (WCAG 2.1)
                used_at: list[str]       # where this pairing appears


            def relative_luminance(rgb: tuple[int, int, int]) -> float:
                """WCAG relative luminance formula. Pure function, easy to unit test."""
                raise NotImplementedError("TODO(brandgen): implement luminance formula")


            def contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
                """WCAG contrast ratio between two RGB colors. Returns 1.0 to 21.0."""
                raise NotImplementedError("TODO(brandgen): implement contrast ratio formula")


            def compute_contrast_matrix(colors: list[str], pairings: list[tuple[str, str]]) -> list[ContrastResult]:
                """Compute contrast for every observed foreground/background pair."""
                raise NotImplementedError("TODO(brandgen): implement matrix computation")
        '''),
    ),

    # ---------- aggregator ----------
    "brandgen/aggregator/__init__.py": "",

    "brandgen/aggregator/merger.py": _stub(
        "Merge per-page extraction outputs into one site-wide brand profile.",
        dedent('''\
            from pydantic import BaseModel

            from brandgen.extractors.buttons import ExtractedButton
            from brandgen.extractors.colors import ExtractedColor
            from brandgen.extractors.contrast import ContrastResult
            from brandgen.extractors.fonts import ExtractedFont
            from brandgen.extractors.logo import LogoCandidate


            class BrandProfile(BaseModel):
                """The aggregated, deduplicated brand data ready for rendering."""
                client_slug: str
                source_pages: list[str]
                colors: list[ExtractedColor]
                fonts: list[ExtractedFont]
                buttons: list[ExtractedButton]
                logo_candidates: list[LogoCandidate]
                contrast_results: list[ContrastResult]


            def merge_extractions(per_page: list[dict], client_slug: str) -> BrandProfile:
                """Combine per-page extractor outputs into one BrandProfile.

                Dedup rules:
                - Colors: bucket by Lab distance, sum frequencies
                - Fonts: union weights/sizes per family
                - Buttons: re-cluster across pages (a primary CTA on page 1 and
                  page 5 should be the same entry, not two separate ones)
                - Logos: pick the top candidate by confidence
                """
                raise NotImplementedError("TODO(brandgen): implement cross-page merge")
        '''),
    ),

    # ---------- renderer ----------
    "brandgen/renderer/__init__.py": "",

    "brandgen/renderer/doc_builder.py": _stub(
        "Render the final HTML brand doc and brand.json from a BrandProfile.",
        dedent('''\
            from pathlib import Path

            from brandgen.aggregator.merger import BrandProfile


            def render_brand_doc(profile: BrandProfile, output_dir: Path) -> Path:
                """Produce branding-doc.html using the Jinja2 template.

                The output mirrors the Premier Remodel reference doc:
                - Color swatches (5-8 colors with hex, RGB, role notes)
                - Typography section (headings, body, samples in real fonts)
                - Buttons (all variants with hover states)
                - WCAG/ADA contrast notes
                - Empty Brand Voice & Identity placeholder for LLM workflow
                - Print-ready CSS with sensible page-break rules

                Also writes brand.json sidecar for programmatic consumption.
                """
                raise NotImplementedError("TODO(brandgen): implement doc renderer")


            def write_brand_json(profile: BrandProfile, output_dir: Path) -> Path:
                """Dump the full BrandProfile as JSON for LLM/programmatic use."""
                raise NotImplementedError("TODO(brandgen): implement JSON writer")
        '''),
    ),

    "brandgen/renderer/templates/brand_doc.html.j2": dedent('''\
        {# ----------------------------------------------------------------- #}
        {# brandgen brand style guide template                               #}
        {# ----------------------------------------------------------------- #}
        {# Modeled on the Premier Remodel reference doc.                     #}
        {# Will be filled out as the renderer module is built.               #}
        {# Print-friendly: page-break rules and color-adjust:exact required. #}
        {# ----------------------------------------------------------------- #}
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>{{ display_name | default(client_slug) }} | Brand Style Guide</title>
            {# TODO(brandgen): full template — stub for now #}
        </head>
        <body>
            <h1>{{ display_name | default(client_slug) }} | Brand Style Guide</h1>
            <p>This template is a stub. See brandgen/renderer/doc_builder.py.</p>
        </body>
        </html>
    '''),

    # =========================================================================
    # tests
    # =========================================================================

    "tests/__init__.py": "",

    "tests/conftest.py": dedent('''\
        """
        Shared pytest fixtures.

        Each extractor will get fixtures here that load known-good HTML/CSS
        snippets from tests/fixtures/ so tests are deterministic and don't
        require live network calls.
        """
        from __future__ import annotations

        from pathlib import Path

        import pytest


        @pytest.fixture
        def fixtures_dir() -> Path:
            """Absolute path to tests/fixtures/."""
            return Path(__file__).parent / "fixtures"
    '''),

    "tests/fixtures/.gitkeep": "",

    "tests/test_input_parser.py": dedent('''\
        """Tests for crawler.input_parser."""
        import pytest


        @pytest.mark.skip(reason="TODO(brandgen): implement after input_parser is built")
        def test_parse_input_detects_csv():
            pass


        @pytest.mark.skip(reason="TODO(brandgen): implement after input_parser is built")
        def test_parse_input_detects_sitemap():
            pass


        @pytest.mark.skip(reason="TODO(brandgen): implement after input_parser is built")
        def test_parse_input_treats_unknown_as_single_url():
            pass
    '''),

    "tests/test_page_selector.py": dedent('''\
        """Tests for crawler.page_selector."""
        import pytest


        @pytest.mark.skip(reason="TODO(brandgen): implement after page_selector is built")
        def test_homepage_always_selected():
            pass


        @pytest.mark.skip(reason="TODO(brandgen): implement after page_selector is built")
        def test_priority_patterns_score_correctly():
            pass


        @pytest.mark.skip(reason="TODO(brandgen): implement after page_selector is built")
        def test_max_pages_cap_enforced():
            pass
    '''),

    "tests/test_colors.py": dedent('''\
        """Tests for extractors.colors."""
        import pytest


        @pytest.mark.skip(reason="TODO(brandgen): implement after colors extractor is built")
        def test_top_n_colors_returned():
            pass


        @pytest.mark.skip(reason="TODO(brandgen): implement after colors extractor is built")
        def test_near_duplicate_colors_merged():
            pass
    '''),

    "tests/test_fonts.py": dedent('''\
        """Tests for extractors.fonts."""
        import pytest


        @pytest.mark.skip(reason="TODO(brandgen): implement after fonts extractor is built")
        def test_font_family_canonical_form():
            pass
    '''),

    "tests/test_buttons.py": dedent('''\
        """Tests for extractors.buttons."""
        import pytest


        @pytest.mark.skip(reason="TODO(brandgen): implement after buttons extractor is built")
        def test_buttons_cluster_by_visual_style():
            pass
    '''),

    "tests/test_logo.py": dedent('''\
        """Tests for extractors.logo."""
        import pytest


        @pytest.mark.skip(reason="TODO(brandgen): implement after logo extractor is built")
        def test_header_logo_ranks_first():
            pass
    '''),

    "tests/test_contrast.py": dedent('''\
        """Tests for extractors.contrast.

        The contrast formulas are pure math from the WCAG spec. These tests
        will be the first real (non-skipped) tests in the project — we can
        validate them with hand-computed values.
        """
        import pytest


        @pytest.mark.skip(reason="TODO(brandgen): implement after contrast module is built")
        def test_pure_white_on_pure_black_is_21():
            pass


        @pytest.mark.skip(reason="TODO(brandgen): implement after contrast module is built")
        def test_known_pairs_match_webaim():
            pass
    '''),

    # =========================================================================
    # Output landing zone
    # =========================================================================

    "brand-guides/.gitkeep": "",
}


# ---------------------------------------------------------------------------
# Scaffold execution
# ---------------------------------------------------------------------------

def write_files(target_dir: Path, force: bool = False) -> tuple[int, int]:
    """Create directories and write all files defined in FILES.

    Returns (created_count, skipped_count).
    """
    created = 0
    skipped = 0

    for rel_path, content in FILES.items():
        dest = target_dir / rel_path
        # Ensure parent directories exist. exist_ok=True is intentional —
        # we want this idempotent.
        dest.parent.mkdir(parents=True, exist_ok=True)

        if dest.exists() and not force:
            print(f"  skip   {rel_path}  (exists, use --force to overwrite)")
            skipped += 1
            continue

        dest.write_text(content, encoding="utf-8")
        print(f"  write  {rel_path}")
        created += 1

    return created, skipped


def validate(target_dir: Path) -> bool:
    """Self-validation pass.

    Two checks:
    1. Every path in FILES actually exists on disk after writing.
    2. The brandgen package can be imported (catches __init__.py mistakes
       and obvious syntax errors in stubs).

    Returns True if everything passes.
    """
    print("\nValidating scaffold...")
    all_ok = True

    # Check 1: file existence
    missing = [p for p in FILES if not (target_dir / p).exists()]
    if missing:
        print(f"  FAIL   {len(missing)} expected files are missing:")
        for m in missing:
            print(f"         - {m}")
        all_ok = False
    else:
        print(f"  OK     all {len(FILES)} expected files present")

    # Check 2: package importability
    # We don't actually import (since dependencies aren't installed yet),
    # but we can confirm the package's __init__.py is syntactically valid
    # by compiling it. This catches typos in the stubs.
    init_path = target_dir / "brandgen" / "__init__.py"
    if init_path.exists():
        try:
            compile(init_path.read_text(), str(init_path), "exec")
            print("  OK     brandgen/__init__.py compiles cleanly")
        except SyntaxError as e:
            print(f"  FAIL   brandgen/__init__.py has a syntax error: {e}")
            all_ok = False

    # Compile-check every Python stub to catch typos in the scaffold itself.
    py_files = [p for p in FILES if p.endswith(".py")]
    syntax_failures = []
    for rel in py_files:
        path = target_dir / rel
        try:
            compile(path.read_text(), str(path), "exec")
        except SyntaxError as e:
            syntax_failures.append((rel, str(e)))

    if syntax_failures:
        print(f"  FAIL   {len(syntax_failures)} Python files failed to compile:")
        for rel, err in syntax_failures:
            print(f"         - {rel}: {err}")
        all_ok = False
    else:
        print(f"  OK     all {len(py_files)} Python stubs compile cleanly")

    return all_ok


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the brandgen project skeleton.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target directory (default: current directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    target.mkdir(parents=True, exist_ok=True)

    print(f"Scaffolding brandgen into: {target}")
    print(f"Force overwrite: {args.force}\n")

    created, skipped = write_files(target, force=args.force)
    print(f"\nWrote {created} files, skipped {skipped}.")

    if not validate(target):
        print("\nScaffold validation FAILED. Check errors above.")
        return 1

    print("\nNext steps:")
    print(f"  cd {target}")
    print("  python -m venv .venv")
    print("  source .venv/bin/activate    # Windows: .venv\\Scripts\\activate")
    print('  pip install -e ".[dev]"')
    print("  playwright install chromium")
    print("  brandgen --help              # confirm the CLI is wired up")
    return 0


if __name__ == "__main__":
    sys.exit(main())