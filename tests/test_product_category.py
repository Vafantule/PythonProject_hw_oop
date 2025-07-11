from unittest.mock import patch

import pytest
from pytest import CaptureFixture, MonkeyPatch

from src.product_category import Category, Product


@pytest.fixture
def sample_product() -> list[Product]:
    return [
        Product("Product1", "Description1", 5000.0, 6),
        Product("Product2", "Description2", 15000.0, 16),
    ]


@pytest.fixture
def category_counters_reset() -> None:
    Category.category_count = 0
    Category.product_count = 0


@pytest.fixture
def sample_category(sample_product: list[Product], category_counters_reset: None) -> Category:
    return Category("Gadgets", "All gadgets", sample_product)


# Тесты для class Product

def test_product() -> None:
    product = Product("TestName", "TestDescription", 999.99, 99)
    assert product.name == "TestName"
    assert product.description == "TestDescription"
    assert product.price == 999.99
    assert product.quantity == 99


def test_product_price_setter_negative(capsys: CaptureFixture[str]) -> None:
    product = Product("Тесты", "Описание", 500.0, 2)
    product.price = -5000
    captured = capsys.readouterr()
    assert "Цена не должна быть нулевая или отрицательная" in captured.out
    assert product.price == 500.0


def test_product_price_lower_confirm_yes(monkeypatch: MonkeyPatch) -> None:
    product = Product("Тесты", "Описание", 500.0, 2)
    monkeypatch.setattr("builtins.input", lambda _: "y")
    product.price = 50
    assert product.price == 50


def test_product_price_lower_confirm_no(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    product = Product("Тесты", "Описание", 500.0, 2)
    monkeypatch.setattr("builtins.input", lambda _: "n")
    product.price = 50
    captured = capsys.readouterr()
    assert "Изменение цены отменено." in captured.out
    assert product.price == 500.0


def test_product_new_product_classmethod() -> None:
    params = {"name": "Kodak", "description": "Ultramax 400", "price": 999.99, "quantity": 13}
    product = Product.new_product(params)
    assert isinstance(product, Product)
    assert product.name == "Kodak"
    assert product.description == "Ultramax 400"
    assert product.price == 999.99
    assert product.quantity == 13


def test_update_or_add_products_add_new() -> None:
    products: list[Product] = []
    product = Product("Xerox", "Secator", 13.0, 2)
    Product.update_or_add_product(products, product)
    assert products[0] is product


def test_update_or_add_products_update_existing() -> None:
    products = [Product("Xerox", "Secator", 13.0, 2)]
    new_product = Product("Xerox", "Secator", 33.0, 12)
    Product.update_or_add_product(products, new_product)
    assert len(products) == 1
    assert products[0].quantity == 14
    assert products[0].price == 33


@pytest.mark.parametrize("name, description, price, quantity", [
    ("Motorola", "Rare phone", 9999.99, 1),
    ("Huawei", "New phone", 29999.99, 3),
    ("Samsung", "Modern phone", 99999.99, 99)
])
def test_parametrized_product_init(name: str, description: str, price: float, quantity: int) -> None:
    product = Product(name, description, price, quantity)
    assert product.name == name
    assert product.description == description
    assert product.price == price
    assert product.quantity == quantity


def test_product_str() -> None:
    product = Product("Тесты", "Описание", 80, 15)
    assert str(product) == "Тесты, 80 руб. Остаток: 15 шт."


def test_product_addition() -> None:
    a = Product("A", "Описание", 100, 10)
    b = Product("B", "Описание", 99, 9)
    assert a + b == 1891
    assert b + a == 1891


def test_product_addition_with_wrong_type() -> None:
    a = Product("A", "Описание", 100, 10)
    with pytest.raises(AttributeError):
        a + 5   # type: ignore[operator]


def test_product_addition_with_none_raises() -> None:
    a = Product("A", "Описание", 100, 10)
    with pytest.raises(AttributeError):
        a + None    # type: ignore[operator]


# Тесты для class Category

def test_category(sample_product: list[Product], category_counters_reset: None) -> None:
    category = Category("Phones", "Accessories", sample_product)
    assert category.name == "Phones"
    assert category.description == "Accessories"
    # assert category.products == sample_product    # # Предыдущее дом.задание.
    assert isinstance(category.products, str)
    for product in sample_product:
        assert product.name in category.products
        assert str(int(product.price)) in category.products


def test_category_class_attributes_count(sample_product: list[Product], category_counters_reset: None) -> None:
    category_1 = Category("Phones", "description_1", sample_product)
    category_2 = Category("TV", "description_2",
                          [Product("TV", "description", 50000.00, 6)])
    assert Category.category_count == 2
    assert Category.product_count == len(sample_product) + 1


def test_category_counter_with_patch(sample_product: list[Product], category_counters_reset: None) -> None:
    with patch.object(Category, "category_count", 50):
        with patch.object(Category, "product_count", 500):
            category = Category("Test", "Test", sample_product)
            assert Category.category_count == 51
            assert Category.product_count == 502

    Category.category_count = 0
    Category.product_count = 0
    category_2 = Category("Test2", "Test2", [])
    assert Category.category_count == 1
    assert Category.product_count == 0


def test_category_add_product(sample_product: list[Product], category_counters_reset: None) -> None:
    category = Category("Phones", "Accessories", [])
    assert Category.product_count == 0
    category.add_product(Product("Тесты", "Описание", 9999.99, 99))
    assert Category.product_count == 1
    assert "Тесты" in category.products


def test_category_product_format(sample_product: list[Product], category_counters_reset: None) -> None:
    category = Category("Phones", "Accessories", sample_product)
    products_str = category.products
    for product in sample_product:
        assert f"{product.name}, {int(product.price)} руб. Остаток: {product.quantity} шт." in products_str


def test_category_products_private(sample_product: list[Product], category_counters_reset: None) -> None:
    category = Category("Phones", "Accessories", sample_product)
    assert isinstance(getattr(type(category), "products", None), property)
    assert hasattr(category, "_Category__products")


def test_category_str(sample_product: list[Product], category_counters_reset: None) -> None:
    category = Category("Phones", "Accessories", sample_product)
    total_quantity = sum(product.quantity for product in sample_product)
    assert str(category) == f"Phones, количество продуктов: {total_quantity} шт."


def test_category_add_product_type_error(category_counters_reset: None) -> None:
    category = Category("Phones", "Accessories", [])
    with pytest.raises(TypeError):
        category.add_product("Данный тип не товар")    # type: ignore[arg-type]


@pytest.mark.parametrize("products, expected", [
    ([Product("A", "Описание", 10, 1),
      Product("B", "Описание", 50, 5)], 1 + 5),
    ([Product("A", "Описание", 10, 2)], 2),
    ([], 0)
])
def test_category_str_quantity_sum(products: list[Product], expected: int, category_counters_reset: None) -> None:
    category = Category("Тестирование", "Тестирование", products)
    assert str(category).endswith(f"{expected} шт.")
