import json

from product_category import Category, Product


def load_categories_from_json(filename: str) -> list[Category]:
    """
    Загрузка категорий и товаров из JSON-файла. Функция.
    :param filename: Входной файл для обработки.
    :return: Список объектов.
    """
    with open(filename, encoding="utf-8") as file:
        data = json.load(file)

    categories: list[Category] = []

    for category_dict in data:
        products = [
            Product(
                name=product.get("name"),
                description=product.get("description"),
                price=product.get("price"),
                quantity=product.get("quantity")
            )
            for product in category_dict.get("products", [])
        ]
        category = Category(
            name=category_dict.get("name"),
            description=category_dict.get("description"),
            products=products
        )
        categories.append(category)
    return categories


if __name__ in "__main__":
    categories = load_categories_from_json("data/products.json")
    for category in categories:
        print(category.name, len(category.products))
