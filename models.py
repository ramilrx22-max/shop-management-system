import re
from datetime import datetime
from typing import List, Optional

class BaseModel:
    """Базовый класс для всех моделей данных.
    
    Attributes
    ----------
    _id : int
        Уникальный идентификатор объекта.
    """
    
    def __init__(self, id: int):
        """Инициализация базовой модели.
        
        Parameters
        ----------
        id : int
            Уникальный идентификатор объекта.
        """
        self._id = id
    
    @property
    def id(self) -> int:
        """Получить идентификатор объекта.
        
        Returns
        -------
        int
            Уникальный идентификатор.
        """
        return self._id
    
    @id.setter
    def id(self, value: int):
        """Установить идентификатор объекта.
        
        Parameters
        ----------
        value : int
            Новый идентификатор.
            
        Raises
        ------
        TypeError
            Если value не является целым числом.
        """
        if not isinstance(value, int):
            raise TypeError("ID must be an integer.")
        self._id = value

class Customer(BaseModel):
    """Класс, представляющий клиента.
    
    Attributes
    ----------
    first_name : str
        Имя клиента.
    last_name : str
        Фамилия клиента.
    email : str
        Электронная почта клиента.
    phone : str
        Номер телефона клиента.
    address : str
        Адрес клиента.
    """
    
    def __init__(self, id: int, first_name: str, last_name: str, email: str, phone: str, address: str):
        """Инициализация клиента.
        
        Parameters
        ----------
        id : int
            Уникальный идентификатор клиента.
        first_name : str
            Имя клиента.
        last_name : str
            Фамилия клиента.
        email : str
            Электронная почта клиента.
        phone : str
            Номер телефона клиента.
        address : str
            Адрес клиента.
        """
        super().__init__(id)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email  # Проверка через сеттер
        self.phone = phone  # Проверка через сеттер
        self.address = address  # Проверка через сеттер
    
    @property
    def email(self) -> str:
        """Получить email клиента.
        
        Returns
        -------
        str
            Электронная почта.
        """
        return self._email
    
    @email.setter
    def email(self, value: str):
        """Установить email с проверкой формата.
        
        Parameters
        ----------
        value : str
            Адрес электронной почты.
            
        Raises
        ------
        ValueError
            Если email не соответствует формату.
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            raise ValueError("Invalid email format.")
        self._email = value
    
    @property
    def phone(self) -> str:
        """Получить номер телефона.
        
        Returns
        -------
        str
            Номер телефона.
        """
        return self._phone
    
    @phone.setter
    def phone(self, value: str):
        """Установить номер телефона с проверкой формата.
        
        Parameters
        ----------
        value : str
            Номер телефона.
            
        Raises
        ------
        ValueError
            Если номер не соответствует формату.
        """
        # Простой паттерн для международных номеров
        pattern = r'^\+?[1-9]\d{1,14}$'
        if not re.match(pattern, value):
            raise ValueError("Invalid phone number format.")
        self._phone = value
    
    @property
    def address(self) -> str:
        """Получить адрес.
        
        Returns
        -------
        str
            Адрес доставки.
        """
        return self._address
    
    @address.setter
    def address(self, value: str):
        """Установить адрес с базовой проверкой.
        
        Parameters
        ----------
        value : str
            Адрес доставки.
            
        Raises
        ------
        ValueError
            Если адрес пустой или слишком короткий.
        """
        if len(value.strip()) < 5:
            raise ValueError("Address is too short.")
        self._address = value
    
    def __str__(self):
        return f"Customer {self.id}: {self.first_name} {self.last_name}"

class Product(BaseModel):
    """Класс, представляющий товар.
    
    Attributes
    ----------
    name : str
        Название товара.
    price : float
        Цена товара.
    category : str
        Категория товара.
    """
    
    def __init__(self, id: int, name: str, price: float, category: str):
        """Инициализация товара.
        
        Parameters
        ----------
        id : int
            Уникальный идентификатор товара.
        name : str
            Название товара.
        price : float
            Цена товара.
        category : str
            Категория товара.
        """
        super().__init__(id)
        self.name = name
        self.price = price
        self.category = category
    
    def __str__(self):
        return f"Product {self.id}: {self.name} ({self.category}) - {self.price} руб."

class Order(BaseModel):
    """Класс, представляющий заказ.
    
    Attributes
    ----------
    customer_id : int
        Идентификатор клиента, оформившего заказ.
    order_date : datetime
        Дата и время заказа.
    status : str
        Статус заказа (например, "в обработке", "доставляется", "завершен").
    items : List[Tuple[Product, int]]
        Список товаров в заказе и их количество.
    """
    
    def __init__(self, id: int, customer_id: int, order_date: Optional[datetime] = None, status: str = "новый"):
        """Инициализация заказа.
        
        Parameters
        ----------
        id : int
            Уникальный идентификатор заказа.
        customer_id : int
            Идентификатор клиента.
        order_date : datetime, optional
            Дата и время заказа. По умолчанию текущее время.
        status : str, optional
            Статус заказа. По умолчанию "новый".
        """
        super().__init__(id)
        self.customer_id = customer_id
        self.order_date = order_date if order_date else datetime.now()
        self.status = status
        self.items = []  # Список кортежей (product, quantity)
    
    def add_product(self, product: Product, quantity: int):
        """Добавить товар в заказ.
        
        Parameters
        ----------
        product : Product
            Объект товара.
        quantity : int
            Количество товара.
            
        Raises
        ------
        ValueError
            Если количество меньше 1.
        """
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
        self.items.append((product, quantity))
    
    def total_cost(self) -> float:
        """Вычислить общую стоимость заказа.
        
        Returns
        -------
        float
            Общая стоимость заказа.
        """
        return sum(product.price * quantity for product, quantity in self.items)
    
    def __str__(self):
        return f"Order {self.id} from {self.order_date} (Status: {self.status})"