"""Перевірити CRUD на mongomock; не замінює перевірку справжнього Atlas."""
from unittest.mock import patch

import mongomock

import verify


if __name__ == "__main__":
    client = mongomock.MongoClient()
    with patch.object(verify, "connect", return_value=(client, client.test_db)):
        verify.main()
