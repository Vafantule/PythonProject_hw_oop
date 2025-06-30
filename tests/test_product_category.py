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


# Тесты для class Category

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
    # Проверяем, что products - property (геттер)
    assert isinstance(getattr(type(category), "products", None), property)
    # Проверяем, что внутренний список действительно приватный
    assert hasattr(category, "_products")
