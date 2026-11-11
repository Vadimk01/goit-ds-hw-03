"""Імпорт JSON до Atlas. Повторний запуск не дублює документи."""
import json
from pathlib import Path

from pymongo import UpdateOne
from pymongo.errors import PyMongoError

from database import connect

ROOT = Path(__file__).resolve().parent


def load_data():
    """Перевірити обидва файли до початку запису в базу."""
    authors = json.loads((ROOT / "authors.json").read_text(encoding="utf-8"))
    quotes = json.loads((ROOT / "qoutes.json").read_text(encoding="utf-8"))
    if not isinstance(authors, list) or not isinstance(quotes, list) or not authors or not quotes:
        raise ValueError("JSON-файли повинні містити непорожні масиви.")
    for author in authors:
        if set(author) != {"fullname", "born_date", "born_location", "description"} or not all(isinstance(v, str) and v.strip() for v in author.values()):
            raise ValueError("Некоректна структура автора.")
    names = {author["fullname"] for author in authors}
    for quote in quotes:
        if set(quote) != {"tags", "author", "quote"} or not isinstance(quote["tags"], list) or not all(isinstance(t, str) for t in quote["tags"]) or not isinstance(quote["quote"], str) or not quote["quote"].strip() or quote["author"] not in names:
            raise ValueError("Некоректна структура цитати або невідомий автор.")
    return authors, quotes


def main():
    client = None
    try:
        authors, quotes = load_data()
        client, db = connect()
        db.authors.create_index("fullname", unique=True)
        db.qoutes.create_index([("author", 1), ("quote", 1)], unique=True)
        for collection, records, keys in ((db.authors, authors, ("fullname",)), (db.qoutes, quotes, ("author", "quote"))):
            result = collection.bulk_write([UpdateOne({key: row[key] for key in keys}, {"$set": row}, upsert=True) for row in records])
            print(f"{collection.name}: додано {result.upserted_count}, змінено {result.modified_count}, усього {collection.count_documents({})}")
    except (OSError, ValueError, TypeError, KeyError, PyMongoError) as exc:
        print(f"Імпорт не завершено ({type(exc).__name__}). Перевірте JSON, .env і доступ до Atlas.")
        return 1
    finally:
        if client is not None:
            client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
