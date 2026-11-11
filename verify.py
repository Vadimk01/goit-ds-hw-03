"""Інтеграційна перевірка CRUD в окремій тимчасовій колекції."""
from uuid import uuid4

from bson import ObjectId

from database import connect
from main import add_feature, create_cat, delete_all, delete_by_name, read_all, read_by_name, update_age


def main():
    client, db = connect()
    collection = db[f"test_cats_{uuid4().hex}"]
    try:
        identifier = create_cat(collection, "barsik", 3, ["рудий"])
        assert isinstance(identifier, ObjectId)
        assert len(read_all(collection)) == 1
        assert read_by_name(collection, "barsik")["age"] == 3
        assert read_by_name(collection, "missing") is None
        assert update_age(collection, "barsik", 4).modified_count == 1
        assert collection.find_one({"_id": identifier})["age"] == 4
        assert update_age(collection, "missing", 4).matched_count == 0
        assert add_feature(collection, "barsik", "лагідний").modified_count == 1
        assert add_feature(collection, "barsik", "лагідний").modified_count == 0
        assert collection.find_one({"_id": identifier})["features"] == ["рудий", "лагідний"]
        for age in (-1, True, "3"):
            try:
                update_age(collection, "barsik", age)
            except ValueError:
                pass
            else:
                raise AssertionError("Прийнято некоректний вік")
        assert delete_by_name(collection, "barsik").deleted_count == 1
        assert delete_by_name(collection, "missing").deleted_count == 0
        create_cat(collection, "a", 1, [])
        create_cat(collection, "b", 2, [])
        assert delete_all(collection).deleted_count == 2
        assert collection.count_documents({}) == 0
        print("Усі CRUD-перевірки пройдено.")
    finally:
        collection.drop()
        client.close()


if __name__ == "__main__":
    main()
