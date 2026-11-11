"""Спільні налаштування підключення до MongoDB."""
import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConfigurationError


def connect():
    """Повернути клієнт і базу; одразу перевірити доступність сервера."""
    load_dotenv(encoding="utf-8-sig")
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise ValueError("Вкажіть MONGODB_URI у файлі .env")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=15000)
    except ConfigurationError:
        raise ValueError("Не вдалося налаштувати MongoDB. Перевірте URI та DNS кластера Atlas.") from None
    try:
        client.admin.command("ping")
    except Exception:
        client.close()
        raise
    return client, client[os.getenv("MONGODB_DATABASE", "goit_ds_hw_03")]
