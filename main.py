import sys

from pymongo.errors import PyMongoError

from db import get_database, handle_db_error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


COLLECTION_NAME = "cats"


def get_cats_collection():
    return get_database()[COLLECTION_NAME]


def create_cat(name: str, age: int, features: list[str]) -> None:
    try:
        result = get_cats_collection().insert_one(
            {"name": name, "age": age, "features": features}
        )
        print(f"Додано кота '{name}' з _id={result.inserted_id}")
    except PyMongoError as exc:
        handle_db_error("створення запису", exc)


def read_all_cats() -> None:
    try:
        cats = list(get_cats_collection().find())
        if not cats:
            print("Колекція порожня.")
            return
        for cat in cats:
            _print_cat(cat)
    except PyMongoError as exc:
        handle_db_error("читання всіх записів", exc)


def read_cat_by_name(name: str) -> None:
    try:
        cat = get_cats_collection().find_one({"name": name})
        if cat is None:
            print(f"Кота з ім'ям '{name}' не знайдено.")
            return
        _print_cat(cat)
    except PyMongoError as exc:
        handle_db_error("пошуку кота за ім'ям", exc)


def update_cat_age(name: str, new_age: int) -> None:
    try:
        result = get_cats_collection().update_one(
            {"name": name}, {"$set": {"age": new_age}}
        )
        if result.matched_count == 0:
            print(f"Кота з ім'ям '{name}' не знайдено.")
            return
        print(f"Вік кота '{name}' оновлено до {new_age}.")
    except PyMongoError as exc:
        handle_db_error("оновлення віку", exc)


def add_cat_feature(name: str, feature: str) -> None:
    try:
        result = get_cats_collection().update_one(
            {"name": name}, {"$addToSet": {"features": feature}}
        )
        if result.matched_count == 0:
            print(f"Кота з ім'ям '{name}' не знайдено.")
            return
        if result.modified_count == 0:
            print(f"Характеристика '{feature}' вже є у кота '{name}'.")
            return
        print(f"Коту '{name}' додано характеристику '{feature}'.")
    except PyMongoError as exc:
        handle_db_error("додавання характеристики", exc)


def delete_cat_by_name(name: str) -> None:
    try:
        result = get_cats_collection().delete_one({"name": name})
        if result.deleted_count == 0:
            print(f"Кота з ім'ям '{name}' не знайдено.")
            return
        print(f"Кота '{name}' видалено.")
    except PyMongoError as exc:
        handle_db_error("видалення кота", exc)


def delete_all_cats() -> None:
    try:
        result = get_cats_collection().delete_many({})
        print(f"Видалено записів: {result.deleted_count}.")
    except PyMongoError as exc:
        handle_db_error("видалення всіх записів", exc)


def seed_sample_cats() -> None:
    try:
        collection = get_cats_collection()
        if collection.count_documents({}) > 0:
            print("Колекція вже містить записи. Сід пропущено.")
            return
        samples = [
            {
                "name": "barsik",
                "age": 3,
                "features": ["ходить в капці", "дає себе гладити", "рудий"],
            },
            {
                "name": "murzik",
                "age": 5,
                "features": ["любить рибу", "спить на клавіатурі"],
            },
            {
                "name": "simba",
                "age": 2,
                "features": ["грається з м'ячиком", "білий"],
            },
        ]
        result = collection.insert_many(samples)
        print(f"Додано зразкових котів: {len(result.inserted_ids)}.")
    except PyMongoError as exc:
        handle_db_error("заповнення зразковими даними", exc)


def _print_cat(cat: dict) -> None:
    features = ", ".join(cat.get("features") or [])
    print(
        f"_id: {cat.get('_id')}\n"
        f"name: {cat.get('name')}\n"
        f"age: {cat.get('age')}\n"
        f"features: [{features}]\n"
    )


def _prompt_int(message: str) -> int | None:
    raw = input(message).strip()
    try:
        return int(raw)
    except ValueError:
        print("Потрібно ввести ціле число.")
        return None


def run_menu() -> None:
    actions = {
        "1": "Показати всіх котів",
        "2": "Знайти кота за ім'ям",
        "3": "Оновити вік кота",
        "4": "Додати характеристику коту",
        "5": "Видалити кота за ім'ям",
        "6": "Видалити всіх котів",
        "7": "Додати нового кота",
        "8": "Заповнити колекцію зразковими даними",
        "0": "Вихід",
    }

    while True:
        print("\n=== Коти в MongoDB ===")
        for key, title in actions.items():
            print(f"{key}. {title}")
        choice = input("Оберіть дію: ").strip()

        if choice == "0":
            print("До побачення.")
            break
        if choice == "1":
            read_all_cats()
        elif choice == "2":
            name = input("Ім'я кота: ").strip()
            read_cat_by_name(name)
        elif choice == "3":
            name = input("Ім'я кота: ").strip()
            age = _prompt_int("Новий вік: ")
            if age is not None:
                update_cat_age(name, age)
        elif choice == "4":
            name = input("Ім'я кота: ").strip()
            feature = input("Нова характеристика: ").strip()
            add_cat_feature(name, feature)
        elif choice == "5":
            name = input("Ім'я кота: ").strip()
            delete_cat_by_name(name)
        elif choice == "6":
            confirm = input("Видалити ВСІ записи? (yes/no): ").strip().lower()
            if confirm == "yes":
                delete_all_cats()
        elif choice == "7":
            name = input("Ім'я: ").strip()
            age = _prompt_int("Вік: ")
            if age is None:
                continue
            raw_features = input("Характеристики через кому: ").strip()
            features = [item.strip() for item in raw_features.split(",") if item.strip()]
            create_cat(name, age, features)
        elif choice == "8":
            seed_sample_cats()
        else:
            print("Невідома команда.")


if __name__ == "__main__":
    try:
        run_menu()
    except PyMongoError as exc:
        handle_db_error("підключення до бази даних", exc)
    except KeyboardInterrupt:
        print("\nРоботу перервано.")
