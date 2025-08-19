import unittest
from datetime import datetime
from models import Customer, Product, Order

class TestModels(unittest.TestCase):
    """Тесты для моделей данных."""
    
    def test_customer_creation(self):
        """Тест создания клиента с валидными данными."""
        customer = Customer(1, "Иван", "Иванов", "test@example.com", "+79123456789", "Москва, ул. Пушкина, д.1")
        self.assertEqual(customer.first_name, "Иван")
        self.assertEqual(customer.last_name, "Иванов")
        self.assertEqual(customer.email, "test@example.com")
        self.assertEqual(customer.phone, "+79123456789")
        self.assertEqual(customer.address, "Москва, ул. Пушкина, д.1")
    
    def test_customer_invalid_email(self):
        """Тест создания клиента с невалидным email."""
        with self.assertRaises(ValueError):
            Customer(1, "Иван", "Иванов", "invalid-email", "+79123456789", "Москва")
    
    def test_customer_invalid_phone(self):
        """Тест создания клиента с невалидным телефоном."""
        with self.assertRaises(ValueError):
            Customer(1, "Иван", "Иванов", "test@example.com", "invalid-phone", "Москва")
    
    def test_customer_invalid_address(self):
        """Тест создания клиента с невалидным адресом."""
        with self.assertRaises(ValueError):
            Customer(1, "Иван", "Иванов", "test@example.com", "+79123456789", "")
    
    def test_product_creation(self):
        """Тест создания товара."""
        product = Product(1, "Ноутбук", 50000.0, "Электроника")
        self.assertEqual(product.name, "Ноутбук")
        self.assertEqual(product.price, 50000.0)
        self.assertEqual(product.category, "Электроника")
    
    def test_order_creation(self):
        """Тест создания заказа."""
        order = Order(1, 1)
        self.assertEqual(order.customer_id, 1)
        self.assertEqual(order.status, "новый")
        self.assertIsInstance(order.order_date, datetime)
        self.assertEqual(len(order.items), 0)
    
    def test_order_add_product(self):
        """Тест добавления товара в заказ."""
        order = Order(1, 1)
        product = Product(1, "Ноутбук", 50000.0, "Электроника")
        order.add_product(product, 2)
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0][0], product)
        self.assertEqual(order.items[0][1], 2)
    
    def test_order_total_cost(self):
        """Тест расчета общей стоимости заказа."""
        order = Order(1, 1)
        product1 = Product(1, "Ноутбук", 50000.0, "Электроника")
        product2 = Product(2, "Мышь", 1000.0, "Электроника")
        order.add_product(product1, 1)
        order.add_product(product2, 2)
        self.assertEqual(order.total_cost(), 50000.0 + 2000.0)
    
    def test_order_add_invalid_quantity(self):
        """Тест добавления товара с невалидным количеством."""
        order = Order(1, 1)
        product = Product(1, "Ноутбук", 50000.0, "Электроника")
        with self.assertRaises(ValueError):
            order.add_product(product, 0)

if __name__ == "__main__":
    unittest.main()