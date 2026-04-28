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
source .venv/bin/activate    # Windows: .venv\Scripts\activate

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
