"""Завдання 1: інтерактивні CRUD-операції з колекцією cats."""
import json

from pymongo.errors import PyMongoError

from database import connect


def create_cat(collection, name, age, features):
    """Створити кота. MongoDB автоматично призначає ObjectId."""
    name = name.strip()
    if not name or isinstance(age, bool) or not isinstance(age, int) or age < 0:
        raise ValueError("Потрібне непорожнє ім'я та цілий невід'ємний вік.")
    if not isinstance(features, list) or any(not isinstance(x, str) or not x.strip() for x in features):
        raise ValueError("Характеристики мають бути списком непорожніх рядків.")
    return collection.insert_one({"name": name, "age": age, "features": [x.strip() for x in features]}).inserted_id


def read_all(collection):
    """Вивести та повернути всі документи."""
    records = list(collection.find())
    print(json.dumps(records, ensure_ascii=False, indent=2, default=str))
    return records


def read_by_name(collection, name):
    """Вивести інформацію про кота за ім'ям."""
    record = collection.find_one({"name": name.strip()})
    print(json.dumps(record, ensure_ascii=False, indent=2, default=str) if record else "Кота не знайдено.")
    return record


def update_age(collection, name, age):
    """Оновити вік кота за ім'ям."""
    if isinstance(age, bool) or not isinstance(age, int) or age < 0:
        raise ValueError("Вік має бути цілим невід'ємним числом.")
    return collection.update_one({"name": name.strip()}, {"$set": {"age": age}})


def add_feature(collection, name, feature):
    """Додати характеристику без дублювання вже наявної."""
    if not feature.strip():
        raise ValueError("Характеристика не може бути порожньою.")
    return collection.update_one({"name": name.strip()}, {"$addToSet": {"features": feature.strip()}})


def delete_by_name(collection, name):
    """Видалити одного кота за ім'ям."""
    return collection.delete_one({"name": name.strip()})


def delete_all(collection):
    """Видалити всі документи колекції cats."""
    return collection.delete_many({})


def main():
    client = None
    try:
        client, db = connect()
        cats = db.cats
        while True:
            print("\n1 — Додати кота\n2 — Усі коти\n3 — Знайти за ім'ям\n4 — Змінити вік\n5 — Додати характеристику\n6 — Видалити кота\n7 — Видалити всіх\n0 — Вихід")
            choice = input("Оберіть дію: ").strip()
            try:
                if choice == "0":
                    break
                if choice == "1":
                    name = input("Ім'я: ")
                    age = int(input("Вік: "))
                    features = [x.strip() for x in input("Характеристики через кому: ").split(",") if x.strip()]
                    print("Створено:", create_cat(cats, name, age, features))
                elif choice == "2":
                    read_all(cats)
                elif choice == "3":
                    read_by_name(cats, input("Ім'я: "))
                elif choice in {"4", "5"}:
                    name = input("Ім'я: ")
                    result = update_age(cats, name, int(input("Новий вік: "))) if choice == "4" else add_feature(cats, name, input("Характеристика: "))
                    print(f"Знайдено: {result.matched_count}; змінено: {result.modified_count}")
                elif choice == "6":
                    print("Видалено:", delete_by_name(cats, input("Ім'я: ")).deleted_count)
                elif choice == "7":
                    if input("Введіть ТАК для видалення всіх котів: ") == "ТАК":
                        print("Видалено:", delete_all(cats).deleted_count)
                else:
                    print("Невідома дія.")
            except (ValueError, PyMongoError) as exc:
                print(f"Помилка операції ({type(exc).__name__}). Перевірте введені дані та доступ до бази.")
    except (ValueError, PyMongoError) as exc:
        print(f"Не вдалося підключитися ({type(exc).__name__}). Перевірте .env і доступ до Atlas.")
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nРоботу завершено.")
    finally:
        if client is not None:
            client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
