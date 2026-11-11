"""Завдання 2: цитати з усіх сторінок та унікальні біографії авторів."""
import json
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parent
BASE_URL = "https://quotes.toscrape.com/"


def get_page(session, url):
    """Завантажити сторінку з таймаутом і перевіркою HTTP-статусу."""
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def scrape():
    """Пройти пагінацію та відвідати кожну сторінку автора один раз."""
    quotes, authors, visited = [], {}, set()
    url = BASE_URL
    with requests.Session() as session:
        session.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))
        while url:
            if url in visited:
                raise ValueError("Виявлено цикл пагінації")
            visited.add(url)
            page = get_page(session, url)
            blocks = page.select("div.quote")
            if not blocks:
                raise ValueError(f"На сторінці немає цитат: {url}")
            for block in blocks:
                author_url = urljoin(url, block.select_one('a[href*="/author/"]')["href"])
                if author_url not in authors:
                    bio = get_page(session, author_url)
                    authors[author_url] = {
                        "fullname": bio.select_one(".author-title").get_text(strip=True),
                        "born_date": bio.select_one(".author-born-date").get_text(strip=True),
                        "born_location": bio.select_one(".author-born-location").get_text(strip=True),
                        "description": bio.select_one(".author-description").get_text(strip=True),
                    }
                quotes.append({
                    "tags": [tag.get_text(strip=True) for tag in block.select(".tags a.tag")],
                    "author": authors[author_url]["fullname"],
                    "quote": block.select_one(".text").get_text(strip=True),
                })
            print(f"Сторінка {len(visited)}: {len(quotes)} цитат, {len(authors)} авторів", flush=True)
            next_link = page.select_one("li.next a")
            url = urljoin(url, next_link["href"]) if next_link else None
    for filename, data in (("qoutes.json", quotes), ("authors.json", list(authors.values()))):
        (ROOT / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return quotes, list(authors.values())


if __name__ == "__main__":
    try:
        scrape()
    except (requests.RequestException, ValueError, AttributeError, TypeError, OSError) as exc:
        raise SystemExit(f"Не вдалося виконати скрапінг: {exc}") from None
