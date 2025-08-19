import sqlite3
import json
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from models import Customer, Product, Order

class Database:
    """Класс для работы с базой данных SQLite.
    
    Attributes
    ----------
    conn : sqlite3.Connection
        Подключение к базе данных.
    cursor : sqlite3.Cursor
        Курсор для выполнения SQL-запросов.
    """
    
    def __init__(self, db_name: str = "shop.db"):
        """Инициализация подключения к базе данных.
        
        Parameters
        ----------
        db_name : str, optional
            Имя файла базы данных. По умолчанию "shop.db".
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Установить подключение к базе данных."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row  # Для доступа к столбцам по имени
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
    
    def create_tables(self):
        """Создать таблицы в базе данных, если они не существуют."""
        try:
            # Таблица клиентов
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT NOT NULL,
                    address TEXT NOT NULL
                )
            """)
            
            # Таблица товаров
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    category TEXT NOT NULL
                )
            """)
            
            # Таблица заказов
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    order_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            """)
            
            # Таблица элементов заказа (связь многие-ко-многим)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    PRIMARY KEY (order_id, product_id),
                    FOREIGN KEY (order_id) REFERENCES orders (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """)
            
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка создания таблиц: {e}")
    
    # --- Методы для работы с клиентами ---
    def add_customer(self, customer: Customer) -> int:
        """Добавить клиента в базу данных.
        
        Parameters
        ----------
        customer : Customer
            Объект клиента для добавления.
            
        Returns
        -------
        int
            ID добавленного клиента.
        """
        try:
            self.cursor.execute(
                "INSERT INTO customers (first_name, last_name, email, phone, address) VALUES (?, ?, ?, ?, ?)",
                (customer.first_name, customer.last_name, customer.email, customer.phone, customer.address)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка добавления клиента: {e}")
            return -1
    
    def get_all_customers(self) -> List[Customer]:
        """Получить всех клиентов из базы данных.
        
        Returns
        -------
        List[Customer]
            Список всех клиентов.
        """
        try:
            self.cursor.execute("SELECT * FROM customers")
            rows = self.cursor.fetchall()
            return [Customer(row['id'], row['first_name'], row['last_name'], 
                           row['email'], row['phone'], row['address']) for row in rows]
        except sqlite3.Error as e:
            print(f"Ошибка получения клиентов: {e}")
            return []
    
    # --- Методы для работы с товарами ---
    def add_product(self, product: Product) -> int:
        """Добавить товар в базу данных.
        
        Parameters
        ----------
        product : Product
            Объект товара для добавления.
            
        Returns
        -------
        int
            ID добавленного товара.
        """
        try:
            self.cursor.execute(
                "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
                (product.name, product.price, product.category)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка добавления товара: {e}")
            return -1
    
    def get_all_products(self) -> List[Product]:
        """Получить все товары из базы данных.
        
        Returns
        -------
        List[Product]
            Список всех товаров.
        """
        try:
            self.cursor.execute("SELECT * FROM products")
            rows = self.cursor.fetchall()
            return [Product(row['id'], row['name'], row['price'], row['category']) for row in rows]
        except sqlite3.Error as e:
            print(f"Ошибка получения товаров: {e}")
            return []
    
    # --- Методы для работы с заказами ---
    def add_order(self, order: Order) -> int:
        """Добавить заказ в базу данных.
        
        Parameters
        ----------
        order : Order
            Объект заказа для добавления.
            
        Returns
        -------
        int
            ID добавленного заказа.
        """
        try:
            # Добавляем заказ
            self.cursor.execute(
                "INSERT INTO orders (customer_id, order_date, status) VALUES (?, ?, ?)",
                (order.customer_id, order.order_date.isoformat(), order.status)
            )
            order_id = self.cursor.lastrowid
            
            # Добавляем элементы заказа
            for product, quantity in order.items:
                self.cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
                    (order_id, product.id, quantity)
                )
            
            self.conn.commit()
            return order_id
        except sqlite3.Error as e:
            print(f"Ошибка добавления заказа: {e}")
            return -1
    
    def get_all_orders(self) -> List[Order]:
        """Получить все заказы из базы данных.
        
        Returns
        -------
        List[Order]
            Список всех заказов.
        """
        try:
            self.cursor.execute("SELECT * FROM orders")
            rows = self.cursor.fetchall()
            
            orders = []
            for row in rows:
                order = Order(row['id'], row['customer_id'], 
                            datetime.fromisoformat(row['order_date']), row['status'])
                
                # Получаем элементы заказа
                self.cursor.execute("""
                    SELECT p.*, oi.quantity 
                    FROM order_items oi 
                    JOIN products p ON oi.product_id = p.id 
                    WHERE oi.order_id = ?
                """, (row['id'],))
                
                items = self.cursor.fetchall()
                for item in items:
                    product = Product(item['id'], item['name'], item['price'], item['category'])
                    order.add_product(product, item['quantity'])
                
                orders.append(order)
            
            return orders
        except sqlite3.Error as e:
            print(f"Ошибка получения заказов: {e}")
            return []
    
    # --- Методы для импорта/экспорта ---
    def export_to_csv(self, table_name: str, filename: str):
        """Экспортировать данные таблицы в CSV файл.
        
        Parameters
        ----------
        table_name : str
            Название таблицы для экспорта.
        filename : str
            Имя файла для сохранения.
        """
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Записываем заголовки
                writer.writerow([description[0] for description in self.cursor.description])
                # Записываем данные
                writer.writerows(rows)
        except (sqlite3.Error, IOError) as e:
            print(f"Ошибка экспорта в CSV: {e}")
    
    def import_from_csv(self, table_name: str, filename: str):
        """Импортировать данные из CSV файла в таблицу.
        
        Parameters
        ----------
        table_name : str
            Название таблицы для импорта.
        filename : str
            Имя файла для загрузки.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader)  # Пропускаем заголовок
                
                placeholders = ', '.join(['?' for _ in headers])
                query = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})"
                
                for row in reader:
                    self.cursor.execute(query, row)
                
                self.conn.commit()
        except (sqlite3.Error, IOError) as e:
            print(f"Ошибка импорта из CSV: {e}")
    
    def export_to_json(self, table_name: str, filename: str):
        """Экспортировать данные таблицы в JSON файл.
        
        Parameters
        ----------
        table_name : str
            Название таблицы для экспорта.
        filename : str
            Имя файла для сохранения.
        """
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()
            
            data = [dict(row) for row in rows]
            
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        except (sqlite3.Error, IOError) as e:
            print(f"Ошибка экспорта в JSON: {e}")
    
    def import_from_json(self, table_name: str, filename: str):
        """Импортировать данные из JSON файла в таблицу.
        
        Parameters
        ----------
        table_name : str
            Название таблицы для импорта.
        filename : str
            Имя файла для загрузки.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                if not data:
                    return
                
                headers = list(data[0].keys())
                placeholders = ', '.join(['?' for _ in headers])
                query = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})"
                
                for item in data:
                    self.cursor.execute(query, [item[header] for header in headers])
                
                self.conn.commit()
        except (sqlite3.Error, IOError, json.JSONDecodeError) as e:
            print(f"Ошибка импорта из JSON: {e}")
    
    def close(self):
        """Закрыть соединение с базой данных."""
        if self.conn:
            self.conn.close()