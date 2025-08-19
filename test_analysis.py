import unittest
import pandas as pd
from unittest.mock import Mock, patch
from analysis import DataAnalyzer

class TestAnalysis(unittest.TestCase):
    """Тесты для модуля анализа данных."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        # Создаем мок базы данных
        self.mock_db = Mock()
        
        # Создаем тестовых клиентов
        self.customers = [
            Mock(id=1, first_name="Иван", last_name="Иванов", email="ivan@example.com", 
                 phone="+79123456789", address="Москва"),
            Mock(id=2, first_name="Петр", last_name="Петров", email="petr@example.com", 
                 phone="+79123456780", address="Санкт-Петербург"),
            Mock(id=3, first_name="Сидор", last_name="Сидоров", email="sidor@example.com", 
                 phone="+79123456781", address="Новосибирск")
        ]
        
        # Создаем тестовые товары
        self.products = [
            Mock(id=1, name="Ноутбук", price=50000.0, category="Электроника"),
            Mock(id=2, name="Мышь", price=1000.0, category="Электроника"),
            Mock(id=3, name="Клавиатура", price=2000.0, category="Электроника")
        ]
        
        # Создаем тестовые заказы
        self.orders = []
        
        # Заказ 1: Иван покупает ноутбук и мышь
        order1 = Mock(id=1, customer_id=1, order_date=pd.Timestamp('2023-01-01'), status="завершен")
        order1.items = [(self.products[0], 1), (self.products[1], 2)]
        self.orders.append(order1)
        
        # Заказ 2: Петр покупает ноутбук и клавиатуру
        order2 = Mock(id=2, customer_id=2, order_date=pd.Timestamp('2023-01-02'), status="завершен")
        order2.items = [(self.products[0], 1), (self.products[2], 1)]
        self.orders.append(order2)
        
        # Заказ 3: Иван снова покупает мышь
        order3 = Mock(id=3, customer_id=1, order_date=pd.Timestamp('2023-01-03'), status="завершен")
        order3.items = [(self.products[1], 1)]
        self.orders.append(order3)
        
        # Настраиваем мок базы данных
        self.mock_db.get_all_customers.return_value = self.customers
        self.mock_db.get_all_products.return_value = self.products
        self.mock_db.get_all_orders.return_value = self.orders
        
        # Создаем анализатор с моком базы данных
        self.analyzer = DataAnalyzer(self.mock_db)
    
    def test_get_orders_dataframe(self):
        """Тест получения DataFrame с заказами."""
        df = self.analyzer.get_orders_dataframe()
        
        # Проверяем, что DataFrame не пустой
        self.assertFalse(df.empty)
        
        # Проверяем количество строк (всего товаров в заказах)
        # order1: 2 товара, order2: 2 товара, order3: 1 товар -> всего 5 строк
        self.assertEqual(len(df), 5)
        
        # Проверяем наличие нужных столбцов
        expected_columns = ['order_id', 'customer_id', 'customer_name', 'order_date', 
                          'status', 'product_id', 'product_name', 'quantity', 'price', 'total']
        self.assertListEqual(list(df.columns), expected_columns)
    
    def test_top_customers_by_orders(self):
        """Тест построения топа клиентов по количеству заказов."""
        # Иван сделал 2 заказа, Петр - 1, Сидор - 0
        fig = self.analyzer.top_customers_by_orders(top_n=2)
        
        # Проверяем, что график создан
        self.assertIsNotNone(fig)
        
        # Можно добавить дополнительные проверки, например, что на графике 2 столбца
        # но это требует более сложного анализа matplotlib figure
    
    def test_orders_dynamics(self):
        """Тест построения динамики заказов."""
        fig = self.analyzer.orders_dynamics(period='D')
        self.assertIsNotNone(fig)
    
    def test_customer_connections_graph(self):
        """Тест построения графа связей клиентов."""
        # Иван и Петр купили общий товар (ноутбук)
        fig = self.analyzer.customer_connections_graph(min_common_products=1)
        self.assertIsNotNone(fig)
    
    def test_sales_by_category(self):
        """Тест построения продаж по категориям."""
        fig = self.analyzer.sales_by_category()
        self.assertIsNotNone(fig)
    
    def test_customer_geography(self):
        """Тест построения географического распределения клиентов."""
        fig = self.analyzer.customer_geography()
        self.assertIsNotNone(fig)

if __name__ == "__main__":
    unittest.main()