class Product:
    """
    Класс, описывающий товар.
    """
    def __init__(self, name: str, description: str, price: float, quantity: int):
        self.name: str = name
        self.description: str = description
        # self.price: float = price    # Предыдущее дом.задание.
        self._price: float = price
        self.quantity: int = quantity

    @property
    def price(self) -> float:
        """
        Геттер для приватного атрибута цены.
        :return:
        """
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        """
        Сеттер для приватного атрибута цены.
        :param value:
        :return:
        """
        # if value > 0:
        #     self._price = value
        # else:
        #     print("Цена не должна быть нулевая или отрицательная")
        if value <= 0:
            print("Цена не должна быть нулевая или отрицательная")
            return

        if value < self._price:
            confirm = input(f"Понизить цену с {self._price} до {value}? ('y'/'n'): ").strip().lower()
            if confirm in ("y", "yes"):
                self._price = value
            else:
                print("Изменение цены отменено.")
        else:
            self._price = value

    @classmethod
    def new_product(cls, params: dict) -> "Product":
        """
        Создание new объекта Product из словаря параметров. Класс-метод.
        :param params:
        :return:
        """
        return cls(
            params.get("name", ""),
            params.get("description", ""),
            params.get("price", 0.0),
            params.get("quantity", 0))

    @staticmethod
    def update_or_add_product(product_list: list["Product"], new_product: "Product") -> None:
        for product in product_list:
            if product.name == new_product.name:
                product.quantity += new_product.quantity
                product.price = max(product.price, new_product.price)
                return
        product_list.append(new_product)


class Category:
    """
    Класс, описывающий категорию товаров.
    """
    category_count: int = 0
    product_count: int = 0

    def __init__(self, name: str, description: str, products: list):
        self.name: str = name
        self.description: str = description
        # self.products: list[Product] = products   # Предыдущее дом.задание.
        self._products: list[Product] = []
        for product in products:
            self.add_product(product)

        Category.category_count += 1
        # Category.product_count += len(products)   # Предыдущее дом.задание.

    def add_product(self, product: Product) -> None:
        """
        Добавляет товар в категорию.
        :param product:
        :return:
        """
        self._products.append(product)
        Category.product_count += 1

    @property
    def products(self) -> str:
        """
        Возвращение копии списка товаров.
        :return:
        """
        # return self.__products.copy()
        return "".join(f"{product.name}, {int(product.price)} руб. Остаток: {product.quantity} шт.\n"
                       for product in self._products)
