from typing import Any
from unittest.mock import patch

import pytest
from pytest import CaptureFixture

from src.product_category import BaseProduct, Category, LawnGrass, LoggerMixin, Product, Smartphone


@pytest.fixture
def sample_product() -> list[Product]:
    return [
        Product("Product1", "Description1", 5000.0, 6),
        Product("Product2", "Description2", 15000.0, 16),
    ]


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


def test_product_price_lower_confirm_yes(monkeypatch: pytest.MonkeyPatch) -> None:
    product = Product("Тесты", "Описание", 500.0, 2)
    monkeypatch.setattr("builtins.input", lambda _: "y")
    product.price = 50
    assert product.price == 50


def test_product_price_lower_confirm_no(monkeypatch: pytest.MonkeyPatch) -> None:
    logs = []

    def fake_print(*args: object) -> None:
        logs.append(str(args[0]))
    product = Product("Тесты", "Описание", 500.0, 2)
    monkeypatch.setattr("builtins.input", lambda _: "n")
    with patch("builtins.print", fake_print):
        product.price = 10.0
    assert any("Изменение цены отменено." in message for message in logs)
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
    assert a + b == 100 * 10 + 9 * 99


def test_product_addition_with_wrong_type() -> None:
    a = Product("A", "Описание", 100, 10)
    with pytest.raises(TypeError):
        _ = a + 5  # type: ignore


def test_product_addition_with_none_raises() -> None:
    a = Product("A", "Описание", 100, 10)
    with pytest.raises(TypeError):
        a + None    # type: ignore[operator]


def test_product_addition_diff_types(sample_smartphone: Smartphone, sample_lawngrass: LawnGrass) -> None:
    with pytest.raises(TypeError):
        _ = sample_lawngrass + sample_smartphone


def test_product_price_private_access() -> None:
    product = Product("Тесты", "Описание", 99.9, 9)
    assert hasattr(product, "_BaseProduct__price")
    assert getattr(product, "_BaseProduct__price") == 99.9


# Тесты для class Category

@pytest.fixture
def category_counters_reset() -> None:
    Category.category_count = 0
    Category.product_count = 0


@pytest.fixture
def sample_category(sample_product: list[Product], category_counters_reset: None) -> Category:
    return Category("Gadgets", "All gadgets", sample_product)


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
    _ = Category("Phones", "description_1", sample_product)
    _ = Category("TV", "description_2",
                 [Product("TV", "description", 50000.00, 6)])
    assert Category.category_count == 2
    assert Category.product_count == len(sample_product) + 1


def test_category_counter_with_patch(sample_product: list[Product], category_counters_reset: None) -> None:
    with patch.object(Category, "category_count", 50):
        with patch.object(Category, "product_count", 500):
            _ = Category("Test", "Test", sample_product)
            assert Category.category_count == 51
            assert Category.product_count == 502

    Category.category_count = 0
    Category.product_count = 0
    _ = Category("Test2", "Test2", [])
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
    category.add_product(Product("Тестовый", "описание", 15, 51))
    assert Category.product_count == 1
    with pytest.raises(TypeError):
        category.add_product("Данный тип не товар")    # type: ignore[arg-type]
    with pytest.raises(TypeError):
        category.add_product(Product)    # type: ignore[arg-type]


@pytest.mark.parametrize("products, expected", [
    ([Product("A", "Описание", 10, 1),
      Product("B", "Описание", 50, 5)], 1 + 5),
    ([Product("A", "Описание", 10, 2)], 2),
    ([], 0)
])
def test_category_str_quantity_sum(products: list[Product], expected: int, category_counters_reset: None) -> None:
    category = Category("Тестирование", "Тестирование", products)
    assert str(category).endswith(f"{expected} шт.")


def test_category_and_smartphone_or_lawngrass_class(category_counters_reset: None) -> None:
    category_1 = Category("Phones", "описание", [])
    category_2 = Category("Grass", "описание", [])
    with pytest.raises(TypeError):
        category_1.add_product(Smartphone)  # type: ignore
    with pytest.raises(TypeError):
        category_2.add_product(LawnGrass)   # type: ignore


def test_category_add_smartphone_and_lawngrass(category_counters_reset: None,
                                               sample_smartphone: Smartphone,
                                               sample_lawngrass: LawnGrass) -> None:
    category = Category("Общий", "описание", [])
    category.add_product(sample_smartphone)
    category.add_product(sample_lawngrass)
    assert "Iphone" in category.products
    assert "Трава зеленая" in category.products


# Тесты для class Smartphone

@pytest.fixture
def sample_smartphone() -> Smartphone:
    return Smartphone("Iphone", "Apple smartphone",
                      180000.00, 13, 99.9, "22 X", 16, "grass")


def test_smartphone_fields(sample_smartphone: Smartphone) -> None:
    smartphone = sample_smartphone
    assert smartphone.efficiency == 99.9
    assert smartphone.model == "22 X"
    assert smartphone.memory == 16
    assert smartphone.color == "grass"


def test_smartphone_str(sample_smartphone: Smartphone) -> None:
    smartphone = sample_smartphone
    expected = "Iphone (22 X, 16, grass, 99.9), 180000 руб. Остаток: 13 шт."
    assert str(smartphone) == expected


def test_smartphone_addition() -> None:
    smartphone_1 = Smartphone("Samsung", "Описание", 5000,
                              13, 99, "S29", 8, "black")
    smartphone_2 = Smartphone("Nokia", "Описание", 500,
                              11, 9, "3311", 64, "white")
    assert smartphone_1 + smartphone_2 == 5000 * 13 + 500 * 11


# Тесты для class LawnGrass

@pytest.fixture
def sample_lawngrass() -> LawnGrass:
    return LawnGrass("Трава зеленая", "Lawn grass",
                     299, 100, "Россия", "2 месяца", "зеленый")


def test_lawngrass_fields(sample_lawngrass: LawnGrass) -> None:
    lawngrass = sample_lawngrass
    assert lawngrass.country == "Россия"
    assert lawngrass.germination_period == "2 месяца"
    assert lawngrass.color == "зеленый"


def test_lawngrass_str(sample_lawngrass: LawnGrass) -> None:
    lawngrass = sample_lawngrass
    expected = "Трава зеленая (Россия, 2 месяца, зеленый), 299 руб. Остаток: 100 шт."
    assert str(lawngrass) == expected


def test_lawngrass_addition() -> None:
    lawngrass_1 = LawnGrass("Трава 1", "Описание", 200,
                            50, "RU", "14 дней", "яркий")
    lawngrass_2 = LawnGrass("Трава 2", "Описание", 400,
                            90, "US", "4 days", "green")
    assert lawngrass_1 + lawngrass_2 == 200 * 50 + 400 * 90


# Тесты для class LoggerMixin

def test_logger_mixin(monkeypatch: pytest.MonkeyPatch) -> None:
    logs: list[str] = []

    def fake_print(*args: object) -> None:
        logs.append(str(args[0]))

    monkeypatch.setattr("builtins.print", fake_print)

    class FakeClassBase:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

    class FakeClass(LoggerMixin, FakeClassBase):
        def __init__(self, aa: int, ab: int, ac: str = "point") -> None:
            super().__init__(aa, ab, ac=ac)

    _ = FakeClass(50, 15, "qwerty")
    assert any("[LoggerMixin] Создан объект класса FakeClass" in message for message in logs)
    assert any("Позиционные: 50, 15; Именованные: ac='qwerty'" in message for message in logs)


@pytest.mark.parametrize("args, kwargs, expected", [
    ((99, ), {}, "Позиционные: 99"),
    ((50, 15), {"ax": "qwerty"}, "Позиционные: 50, 15; Именованные: ax='qwerty'"),
    ((), {"key": "value"}, "Именованные: key='value'"),
])
def test_logger_mixin_parametrized(monkeypatch: pytest.MonkeyPatch,
                                   args: tuple[Any, ...],
                                   kwargs: dict[str, Any],
                                   expected: str) -> None:
    logs: list[str] = []

    def fake_print(*args: object) -> None:
        logs.append(str(args[0]))
    monkeypatch.setattr("builtins.print", fake_print)

    class FakeClassBase:
        def __init__(self, *args: object, **kwargs: object):
            pass

    class FakeClass(LoggerMixin, FakeClassBase):
        def __init__(self, *args: object, **kwargs: object):
            super().__init__(*args, **kwargs)
    FakeClass(*args, **kwargs)
    assert any(expected in message for message in logs)


# Тесты для class BaseProduct

def test_baseproduct_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseProduct("Тестовые", "Описание", 99, 9)  # type: ignore[abstract]


def test_baseproduct_price_property_and_setter() -> None:
    class ConcreteProduct(BaseProduct):
        def __str__(self) -> str:
            return "Тесты"

        @classmethod
        def new_product(cls, params: dict) -> "ConcreteProduct":
            return cls("Тестовые", "Описание", 99, 9)
    product = ConcreteProduct("Тест", "Описание", 99.9, 9)
    assert product.price == 99.9
    product.price = 55.9
    assert product.price == 55.9


def test_baseproduct_price_setter_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    logs: list[str] = []

    def fake_print(*args: object) -> None:
        logs.append(str(args[0]))
    monkeypatch.setattr("builtins.print", fake_print)

    class ConcreteProduct(BaseProduct):
        def __str__(self) -> str:
            return "Тесты"

        @classmethod
        def new_product(cls, params: dict) -> "ConcreteProduct":
            return cls("Тестовые", "Описание", 99, 9)

    product: ConcreteProduct = ConcreteProduct("Тест", "Описание", 99.9, 9)
    product.price = -50.5
    assert any("Цена не должна быть нулевая или отрицательная" in message for message in logs)
    assert product.price == 99.9
