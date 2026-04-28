# brandgen Build Order

Implementation checklist. Work top to bottom. **Do not move past a validation gate until it passes.**

For full architectural context, see `ARCHITECTURE.md`. That document is the source of truth for what each file should do — this one only tracks order and progress.

## Status Legend

- `[ ]` Not started
- `[~]` In progress
- `[x]` Complete and validated
- `[!]` Blocked — needs architect (Claude) input before proceeding

---

## Phase 1: Foundation (pure math, no I/O)

Pure functions, easiest to test. Builds confidence in the toolchain before anything depends on external systems.

- `[ ]` 1. `brandgen/extractors/contrast.py` — implement `relative_luminance`, `contrast_ratio`, `compute_contrast_matrix`
- `[ ]` 2. `tests/test_contrast.py` — un-skip and write real tests (white-on-black = 21.0, hand-computed pairs match WebAIM calculator)

**Validation gate:** `pytest tests/test_contrast.py -v` shows all tests passing. This proves the test harness works and gives us math we trust before anything builds on it.

---

## Phase 2: Minimal scraping (one URL, post-JS capture)

Get real-world data flowing into the pipeline. Single-page only at this stage — no CSV, no sitemap.

- `[ ]` 3. `brandgen/scraper/style_capture.py` — JavaScript that runs inside the browser to capture computed styles for sample selectors
- `[ ]` 4. `brandgen/scraper/playwright_runner.py` — orchestrator that launches Chromium, navigates, runs style_capture, dumps to disk
- `[ ]` 5. `brandgen/cli.py` — fill in `scrape` command (single URL only for now; CSV/sitemap come in Phase 5)

**Validation gate:** `brandgen scrape https://premierremodel.com --client-slug premier-remodel` writes a JSON file to `brand-guides/premier-remodel/captures/` containing computed styles for headings, buttons, and links. Open the JSON manually and confirm real values are present (no nulls, no empty arrays for things that should have data).

---

## Phase 3: Extractors (captured data → typed brand pieces)

One extractor at a time. Each ships with fixture-based tests before moving to the next.

- `[ ]` 6. `brandgen/extractors/colors.py` — top-N color extraction with role tagging
- `[ ]` 7. `tests/test_colors.py` — un-skip with fixture tests
- `[ ]` 8. `brandgen/extractors/fonts.py` — font families, weights, sizes
- `[ ]` 9. `tests/test_fonts.py` — un-skip with fixture tests
- `[ ]` 10. `brandgen/extractors/buttons.py` — variant clustering
- `[ ]` 11. `tests/test_buttons.py` — un-skip with fixture tests
- `[ ]` 12. `brandgen/extractors/logo.py` — heuristic ranking
- `[ ]` 13. `tests/test_logo.py` — un-skip with fixture tests

**Validation gate:** `pytest tests/ -v` runs all extractor tests green. Then a manual sanity test: feed the Phase 2 capture into each extractor in a Python REPL and confirm reasonable output shape.

---

## Phase 4: Aggregation + rendering (first complete brand doc)

Glue everything into a printable HTML document.

- `[ ]` 14. `brandgen/aggregator/merger.py` — single-page version of merge (multi-page comes in Phase 5)
- `[ ]` 15. `brandgen/renderer/templates/brand_doc.html.j2` — full Jinja2 template modeled on the Premier Remodel reference
- `[ ]` 16. `brandgen/renderer/doc_builder.py` — render the template, write `brand.json` sidecar
- `[ ]` 17. `brandgen/cli.py` — wire up `extract`, `render`, and `all` commands

---

## MILESTONE 1: First working proof-of-concept

Run end-to-end against the three test sites:

```powershell
brandgen all https://premierremodel.com --client-slug premier-remodel
brandgen all https://onethingdigital.com --client-slug one-thing-digital
brandgen all https://rakks.com --client-slug rakks
```

Open each generated `branding-doc.html` and diff visually against the Premier Remodel reference doc. Note gaps. Iterate.

**Do not start Phase 5 until the single-page POC produces useful output for all three sites.** If it doesn't, the issue is in Phases 1–4 and adding multi-page support won't fix it.

---

## Phase 5: Multi-page support (CSV and sitemap input)

Expand from one URL to up to 10 pages.

- `[ ]` 18. `brandgen/crawler/input_parser.py` — detect URL/CSV/sitemap, dispatch
- `[ ]` 19. `tests/test_input_parser.py` — un-skip with fixture tests
- `[ ]` 20. `brandgen/crawler/page_selector.py` — priority scoring algorithm
- `[ ]` 21. `tests/test_page_selector.py` — un-skip with fixture tests
- `[ ]` 22. `brandgen/aggregator/merger.py` — extend single-page merge to cross-page deduplication
- `[ ]` 23. `brandgen/cli.py` — extend `scrape` to accept CSV/sitemap inputs

**Validation gate:** Run against a sitemap from one of the test sites. Confirm exactly the priority pages you expect, capped at 10.

---

## Phase 6: Offline rendering (locally-viewable archive)

The "open the HTML locally and see what it looks like online" requirement.

- `[ ]` 24. `brandgen/archiver/asset_downloader.py` — download CSS, fonts, images
- `[ ]` 25. `brandgen/archiver/url_rewriter.py` — rewrite absolute URLs to relative local paths
- `[ ]` 26. `brandgen/scraper/playwright_runner.py` — extend to call the archiver after capture
- `[ ]` 27. `brandgen/archiver/asset_downloader.py` — implement `deduplicate_shared_assets` for `_shared/css/`

**Validation gate:** Open `brand-guides/premier-remodel/site/homepage/index.html` directly in a browser (no server). Compare visually to live site — should match within reason.

---

## Phase 7: Hover states

- `[ ]` 28. `brandgen/scraper/hover_capture.py` — both static CSS parsing and JS-driven Playwright hover simulation
- `[ ]` 29. `brandgen/scraper/playwright_runner.py` — wire hover_capture into the scraper
- `[ ]` 30. `brandgen/extractors/buttons.py` — extend to surface hover states in output
- `[ ]` 31. `brandgen/renderer/templates/brand_doc.html.j2` — render hover states alongside resting states

**Validation gate:** Generated doc shows both normal and hover states for at least the primary CTA on each test site.

---

## Phase 8: Per-client config

- `[ ]` 32. `brandgen/config.py` — implement `load_client_config` and `write_default_client_config` (YAML)
- `[ ]` 33. `brandgen/cli.py` — read config at start of each command, auto-create on first run
- `[ ]` 34. Crawler and extractors — accept `ClientConfig`, respect `ignore_selectors`, `forced_paths`, etc.

**Validation gate:** Edit a generated `config.yaml` to add an ignore selector like `#cookie-banner`. Re-run. Confirm the cookie banner's colors no longer pollute the extracted palette.

---

## Summary

| Phase | Files | What you can demo |
|---|---|---|
| 1 | 2 | Math is right |
| 2 | 3 | Real page captured to JSON |
| 3 | 8 | Extractors work against fixtures |
| 4 | 4 | First brand doc generated |
| **MILESTONE 1** | — | **End-to-end POC working on three test sites** |
| 5 | 6 | Multi-page sitemap input |
| 6 | 4 (3 extending) | Offline-viewable archive |
| 7 | 4 (3 extending) | Hover states captured |
| 8 | 3 (2 extending) | Per-client config working |

Total: 34 file actions across 8 phases. Phases 1–4 are the critical path; everything after is layered enhancement.

---

## Notes / Architect Decisions Log

Use this section to record decisions made mid-build that diverge from the original plan. Helps when re-running this process for future tools.

- _(empty — add entries with date and rationale as decisions arise)_
