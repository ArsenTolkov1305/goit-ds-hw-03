import json
from pathlib import Path

from pymongo.errors import PyMongoError

from db import get_database, handle_db_error

BASE_DIR = Path(__file__).resolve().parent
AUTHORS_FILE = BASE_DIR / "authors.json"
QUOTES_FILE = BASE_DIR / "qoutes.json"


def load_json(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"Файл {path.name} не знайдено. Спочатку запустіть: python scrape_quotes.py"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def import_collection(name: str, documents: list[dict]) -> None:
    collection = get_database()[name]
    collection.delete_many({})
    if not documents:
        print(f"Колекція '{name}': немає даних для імпорту.")
        return
    result = collection.insert_many(documents)
    print(f"Колекція '{name}': імпортовано {len(result.inserted_ids)} документів.")


def main() -> None:
    try:
        authors = load_json(AUTHORS_FILE)
        quotes = load_json(QUOTES_FILE)
        import_collection("authors", authors)
        import_collection("qoutes", quotes)
        print("Імпорт завершено.")
    except FileNotFoundError as exc:
        print(exc)
    except json.JSONDecodeError as exc:
        print(f"Некоректний JSON: {exc}")
    except PyMongoError as exc:
        handle_db_error("імпорту даних", exc)


if __name__ == "__main__":
    main()
