from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator


class LoggerMixin:
    """
    Миксин для логирования информации о создании объекта.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Логирование создание объекта.
        """
        class_name: str = self.__class__.__name__
        params_str: str = ""
        if args:
            params_str += "Позиционные: " + ", ".join(repr(arg) for arg in args)
        if kwargs:
            if params_str:
                params_str += "; "
            params_str += "Именованные: " + ", ".join(f"{key}={value!r}" for key, value in kwargs.items())
        print(f"[LoggerMixin] Создан объект класса {class_name} с параметрами: {params_str}")
        super().__init__(*args, **kwargs)


class BaseProduct(ABC):
    """
    Абстрактный базовый класс для всех товаров.
    """
    name: str
    description: str
    __price: float
    quantity: int

    def __init__(self, name: str, description: str, price: float, quantity: int) -> None:
        """
        Инициализация базового продукта.
        """
        if quantity == 0:
            raise ValueError("Товар с нулевым количеством не может быть добавлен.")
        self.name: str = name
        self.description: str = description
        self.__price: float = price
        self.quantity: int = quantity

    @property
    def price(self) -> float:
        """
        Геттер для приватного атрибута цены.
        :return:
        """
        return self.__price

    @price.setter
    def price(self, value: float) -> None:
        """
        Сеттер для приватного атрибута цены.
        """
        if value <= 0:
            print("Цена не должна быть нулевая или отрицательная")
            return
        self.__price = value

    @abstractmethod
    def __str__(self) -> str:
        pass

    @classmethod
    @abstractmethod
    def new_product(cls, params: Dict[str, Any]) -> "BaseProduct":
        pass


class Product(LoggerMixin, BaseProduct):
    """
    Класс, описывающий товар, который наследует базовую функциональность от BaseProduct.
    """
    def __init__(self, name: str, description: str, price: float, quantity: int) -> None:
        """
        Инициализация продукта.
        """
        super().__init__(name, description, price, quantity)

    @property
    def price(self) -> float:
        return super().price

    @price.setter
    def price(self, value: float) -> None:
        """
        Сеттер для приватного атрибута цены.
        """
        if value <= 0:
            print("Цена не должна быть нулевая или отрицательная")
            return

        if value < self._BaseProduct__price:    # type: ignore
            confirm: str = input(f"Понизить цену с {self._BaseProduct__price} "     # type: ignore
                                 f"до {value}? ('y'/'n'): ").strip().lower()
            if confirm in ("y", "yes"):
                self._BaseProduct__price = value
            else:
                print("Изменение цены отменено.")
        else:
            self._BaseProduct__price = value

    @classmethod
    def new_product(cls, params: dict[str, Any]) -> "Product":
        """
        Создание new объекта Product из словаря параметров. Класс-метод.
        """
        return cls(
            params.get("name", ""),
            params.get("description", ""),
            params.get("price", 0.0),
            params.get("quantity", 0))

    @staticmethod
    def update_or_add_product(product_list: list["Product"], new_product: "Product") -> None:
        """
        Обновляет количество существующего продукта или добавляет новый в список.
        """
        for product in product_list:
            if product.name == new_product.name:
                product.quantity += new_product.quantity
                product.price = max(product.price, new_product.price)
                return
        product_list.append(new_product)

    def __str__(self) -> str:
        """
        Строковое представление продукта.
        """
        return f"{self.name}, {int(self.price)} руб. Остаток: {self.quantity} шт."

    def __add__(self, other: "Product") -> float:
        """
        Складывает два товара, одного класса, как сумму их полной стоимости.
        """
        if type(self) is not type(other):
            raise TypeError(f"Нельзя складывать товары разных классов: {type(self).__name__} & {type(other).__name__}")
        return self.price * self.quantity + other.price * other.quantity


class ZeroQuantityError(Exception):
    """
    Исключение выбрасывается, когда пытаются добавить товар с нулевым количеством
    в категорию или заказ.
    """
    def __init__(self, message: str = "Количество товаров должно быть больше нуля"):
        super().__init__(message)


class CategoryIterator:
    """
    Итератор для перебора товаров одной категории.
    """
    def __init__(self, category: "Category") -> None:
        self._products: list[Product] = category._Category__products    # type: ignore[attr-defined]
        self._index: int = 0

    def __iter__(self) -> "CategoryIterator":
        return self

    def __next__(self) -> Product:
        if self._index < len(self._products):
            result: Product = self._products[self._index]
            self._index += 1
            return result
        else:
            raise StopIteration


class BaseCategory(ABC):
    """
    Абстрактный базовый класс для Category.
    """
    name: str
    description: str

    def __init__(self, name: str, description: str) -> None:
        """
        Инициализация базовой категории.
        """
        self.name: str = name
        self.description: str = description

    @abstractmethod
    def __str__(self) -> str:
        """
        Абстрактный метод.
        """
        pass

class Category(LoggerMixin, BaseCategory):
    """
    Класс, описывающий категорию товаров.
    """
    category_count: int = 0
    product_count: int = 0

    def __init__(self, name: str, description: str, products: list["Product"], *args: Any, **kwargs: Any):
        super().__init__(name, description)
        self.__products: list[Product] = []
        for product in products:
            self.add_product(product)
        Category.category_count += 1

    def add_product(self, product: Product) -> None:
        """
        Добавляет товар в категорию.
        """
        try:
            if not isinstance(product, Product):
                if type(product) is type and issubclass(product, Product):
                    raise TypeError("Только экземпляры класса, а не классы продуктов.")
                raise TypeError("Только объекты класса Product или его наследников.")
            if product.quantity == 0:
                raise ZeroQuantityError("Количество товаров должно быть больше нуля")
            self.__products.append(product)
            Category.product_count += 1
            print(f"Товар '{product.name}' успешно добавлен в категорию.")
        except ZeroQuantityError as error:
            print(error)
        finally:
            print("Обработка добавления категорий товара завершена.")

    @property
    def products(self) -> str:
        """
        Возвращение копии списка товаров. Геттер.
        """
        return "".join(f"{product}\n" for product in self.__products)

    def middle_price(self) -> float:
        """
        Считает средний ценник всех товаров категории.
        """
        try:
            total_price: float = sum(product.price for product in self.__products)
            count: int = len(self.__products)
            return total_price / count
        except ZeroDivisionError:
            return 0

    def __str__(self) -> str:
        total_quantity: int = sum(product.quantity for product in self.__products)
        return f"{self.name}, количество продуктов: {total_quantity} шт."

    def __iter__(self) -> Iterator[Product]:
        return CategoryIterator(self)


class Smartphone(Product):
    """
    Класс-наследник от Product для смартфонов.
    """
    def __init__(self, name: str, description: str, price: float, quantity: int,
                 efficiency: float, model: str, memory: int, color: str):
        super().__init__(name, description, price, quantity)
        self.efficiency = efficiency
        self.model = model
        self.memory = memory
        self.color = color

    def __str__(self) -> str:
        return (f"{self.name} ({self.model}, {self.memory}, {self.color}, {self.efficiency}), "
                f"{int(self.price)} руб. Остаток: {self.quantity} шт.")


class LawnGrass(Product):
    """
    Класс-наследник от Product для травы газонной.
    """
    def __init__(self, name: str, description: str, price: float, quantity: int,
                 country: str, germination_period: str, color: str):
        super().__init__(name, description, price, quantity)
        self.country = country
        self.germination_period = germination_period
        self.color = color

    def __str__(self) -> str:
        return (f"{self.name} ({self.country}, {self.germination_period}, {self.color}), "
                f"{int(self.price)} руб. Остаток: {self.quantity} шт.")


class Order(BaseCategory):
    """
    Класс, описывающий заказ на один товар.
    """
    product: "Product"
    quantity: int
    total_price: float

    def __init__(self, name: str, description: str, product: "Product", quantity: int, price: float) -> None:
        super().__init__(name, description)
        try:
            if quantity <= 0:
                raise ZeroQuantityError("Количество товаров должно быть больше нуля")
            self.product: "Product" = product
            self.quantity: int = quantity
            self.total_price: float = product.price * quantity
            print(f"Товар '{product.name}' успешно добавлен в заказ.")
        except ZeroQuantityError as error:
            print(error)
        finally:
            print("Обработка добавления товара, в заказ, завершена.")

    def __str__(self) -> str:
        return (f"Заказ: {self.name}\n"
                f"Описание: {self.description}\n"
                f"Товар: {self.product.name}\n"
                f"Количество: {self.quantity}\n"
                f"Итого: {self.total_price:.2f} руб.")
