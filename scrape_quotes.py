from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urljoin

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://quotes.toscrape.com"
OUTPUT_DIR = Path(__file__).resolve().parent
QUOTES_FILE = OUTPUT_DIR / "qoutes.json"
AUTHORS_FILE = OUTPUT_DIR / "authors.json"


def fetch_html(url: str) -> str:
    response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return response.text


def parse_quotes_page(html: str) -> tuple[list[dict], str | None]:
    soup = BeautifulSoup(html, "lxml")
    quotes: list[dict] = []

    for quote_block in soup.select("div.quote"):
        text = quote_block.select_one("span.text")
        author = quote_block.select_one("small.author")
        author_link = quote_block.select_one("span a")
        tags = [tag.get_text(strip=True) for tag in quote_block.select("div.tags a.tag")]

        quotes.append(
            {
                "tags": tags,
                "author": author.get_text(strip=True) if author else "",
                "quote": text.get_text(strip=True) if text else "",
                "_author_url": urljoin(BASE_URL, author_link["href"])
                if author_link and author_link.has_attr("href")
                else None,
            }
        )

    next_link = soup.select_one("li.next a")
    next_path = next_link["href"] if next_link and next_link.has_attr("href") else None
    return quotes, next_path


def parse_author_page(html: str, fallback_name: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    fullname = soup.select_one("h3.author-title")
    born_date = soup.select_one("span.author-born-date")
    born_location = soup.select_one("span.author-born-location")
    description = soup.select_one("div.author-description")

    return {
        "fullname": fullname.get_text(strip=True) if fullname else fallback_name,
        "born_date": born_date.get_text(strip=True) if born_date else "",
        "born_location": born_location.get_text(strip=True) if born_location else "",
        "description": description.get_text(" ", strip=True) if description else "",
    }


def scrape_all() -> tuple[list[dict], list[dict]]:
    quotes: list[dict] = []
    author_urls: dict[str, str] = {}
    next_path = "/"

    while next_path:
        page_url = urljoin(BASE_URL, next_path)
        print(f"Скрапінг сторінки: {page_url}")
        html = fetch_html(page_url)
        page_quotes, next_path = parse_quotes_page(html)

        for item in page_quotes:
            author_url = item.pop("_author_url", None)
            author_name = item["author"]
            if author_url and author_name not in author_urls:
                author_urls[author_name] = author_url
            quotes.append(item)

    authors: list[dict] = []
    for name, url in author_urls.items():
        print(f"Скрапінг автора: {name}")
        authors.append(parse_author_page(fetch_html(url), name))

    return quotes, authors


def save_json(path: Path, data: list[dict]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Записано {len(data)} записів у {path.name}")


def main() -> None:
    try:
        quotes, authors = scrape_all()
        save_json(QUOTES_FILE, quotes)
        save_json(AUTHORS_FILE, authors)
    except requests.RequestException as exc:
        print(f"Помилка HTTP під час скрапінгу: {exc}")


if __name__ == "__main__":
    main()
