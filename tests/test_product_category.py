from unittest.mock import patch

import pytest

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


def test_product() -> None:
    product = Product("TestName", "TestDescription", 999.99, 99)
    assert product.name == "TestName"
    assert product.description == "TestDescription"
    assert product.price == 999.99
    assert product.quantity == 99


def test_category(sample_product: list[Product], category_counters_reset: None) -> None:
    category = Category("Phones", "Accessories", sample_product)
    assert category.name == "Phones"
    assert category.description == "Accessories"
    assert category.products == sample_product


def test_category_class_attributes_count(sample_product: list[Product], category_counters_reset: None) -> None:
    category_1 = Category("Phones", "description_1", sample_product)
    category_2 = Category("TV", "description_2",
                          [Product("TV", "description", 50000.00, 6)])
    assert Category.category_count == 2
    assert Category.product_count == len(sample_product) + 1


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
