import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

load_dotenv()

DEFAULT_URI = "mongodb://localhost:27017/"
DEFAULT_DB = "homework03"


def get_client() -> MongoClient:
    uri = os.getenv("MONGO_URI", DEFAULT_URI)
    client = MongoClient(uri, serverSelectionTimeoutMS=8000)
    try:
        client.admin.command("ping")
    except ConnectionFailure as exc:
        raise ConnectionFailure(
            "Не вдалося підключитися до MongoDB. "
            "Перевірте MONGO_URI у файлі .env або запустіть Docker: docker compose up -d"
        ) from exc
    return client


def get_database():
    db_name = os.getenv("MONGO_DB", DEFAULT_DB)
    return get_client()[db_name]


def handle_db_error(operation: str, exc: PyMongoError) -> None:
    print(f"Помилка під час {operation}: {exc}")
