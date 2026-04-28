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
