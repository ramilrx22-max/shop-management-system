import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from models import Customer, Product, Order
from db import Database
from analysis import DataAnalyzer

class ShopApp:
    """Главный класс приложения для управления интернет-магазином.
    
    Attributes
    ----------
    root : tk.Tk
        Корневое окно приложения.
    db : Database
        Объект для работы с базой данных.
    analyzer : DataAnalyzer
        Объект для анализа данных.
    notebook : ttk.Notebook
        Виджет с вкладками для различных разделов приложения.
    """
    
    def __init__(self, root):
        """Инициализация приложения.
        
        Parameters
        ----------
        root : tk.Tk
            Корневое окно приложения.
        """
        self.root = root
        self.root.title("Система управления интернет-магазином")
        self.root.geometry("1000x700")
        
        # Инициализация базы данных и анализатора
        self.db = Database()
        self.analyzer = DataAnalyzer(self.db)
        
        # Создание виджета с вкладками
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Создание вкладок
        self.create_customers_tab()
        self.create_products_tab()
        self.create_orders_tab()
        self.create_analysis_tab()
        self.create_import_export_tab()
        
        # Обновление данных при запуске
        self.update_customers_list()
        self.update_products_list()
        self.update_orders_list()
    
    def create_customers_tab(self):
        """Создать вкладку для работы с клиентами."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Клиенты")
        
        # Панель добавления клиента
        add_frame = ttk.LabelFrame(frame, text="Добавить клиента")
        add_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(add_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.first_name_entry = ttk.Entry(add_frame)
        self.first_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Фамилия:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.last_name_entry = ttk.Entry(add_frame)
        self.last_name_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.email_entry = ttk.Entry(add_frame)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Телефон:").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.phone_entry = ttk.Entry(add_frame)
        self.phone_entry.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Адрес:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.address_entry = ttk.Entry(add_frame, width=50)
        self.address_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky='we')
        
        ttk.Button(add_frame, text="Добавить", command=self.add_customer).grid(
            row=3, column=0, columnspan=4, pady=10)
        
        # Список клиентов
        list_frame = ttk.LabelFrame(frame, text="Список клиентов")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ("id", "first_name", "last_name", "email", "phone", "address")
        self.customers_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Определение заголовков
        self.customers_tree.heading("id", text="ID")
        self.customers_tree.heading("first_name", text="Имя")
        self.customers_tree.heading("last_name", text="Фамилия")
        self.customers_tree.heading("email", text="Email")
        self.customers_tree.heading("phone", text="Телефон")
        self.customers_tree.heading("address", text="Адрес")
        
        # Настройка столбцов
        self.customers_tree.column("id", width=50)
        self.customers_tree.column("first_name", width=100)
        self.customers_tree.column("last_name", width=100)
        self.customers_tree.column("email", width=150)
        self.customers_tree.column("phone", width=120)
        self.customers_tree.column("address", width=200)
        
        # Добавление scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.customers_tree.pack(side='left', fill='both', expand=True)
        
        # Кнопки управления
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="Обновить", command=self.update_customers_list).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_customer).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Поиск", command=self.search_customers).pack(side='left', padx=5)
        
        # Поле поиска
        search_frame = ttk.Frame(btn_frame)
        search_frame.pack(side='left', padx=10)
        
        ttk.Label(search_frame, text="Поиск:").pack(side='left')
        self.customer_search_entry = ttk.Entry(search_frame, width=20)
        self.customer_search_entry.pack(side='left', padx=5)
        self.customer_search_entry.bind('<Return>', lambda e: self.search_customers())
    
    def create_products_tab(self):
        """Создать вкладку для работы с товарами."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Товары")
        
        # Панель добавления товара
        add_frame = ttk.LabelFrame(frame, text="Добавить товар")
        add_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(add_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.product_name_entry = ttk.Entry(add_frame)
        self.product_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Цена:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.product_price_entry = ttk.Entry(add_frame)
        self.product_price_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Категория:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.product_category_entry = ttk.Entry(add_frame)
        self.product_category_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(add_frame, text="Добавить", command=self.add_product).grid(
            row=2, column=0, columnspan=4, pady=10)
        
        # Список товаров
        list_frame = ttk.LabelFrame(frame, text="Список товаров")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ("id", "name", "price", "category")
        self.products_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Определение заголовков
        self.products_tree.heading("id", text="ID")
        self.products_tree.heading("name", text="Название")
        self.products_tree.heading("price", text="Цена")
        self.products_tree.heading("category", text="Категория")
        
        # Настройка столбцов
        self.products_tree.column("id", width=50)
        self.products_tree.column("name", width=200)
        self.products_tree.column("price", width=100)
        self.products_tree.column("category", width=150)
        
        # Добавление scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.products_tree.pack(side='left', fill='both', expand=True)
        
        # Кнопки управления
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="Обновить", command=self.update_products_list).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_product).pack(side='left', padx=5)
    
    def create_orders_tab(self):
        """Создать вкладку для работы с заказами."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Заказы")
        
        # Панель создания заказа
        add_frame = ttk.LabelFrame(frame, text="Создать заказ")
        add_frame.pack(fill='x', padx=5, pady=5)
        
        # Выбор клиента
        ttk.Label(add_frame, text="Клиент:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(add_frame, textvariable=self.customer_var, state='readonly')
        self.customer_combo.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        
        # Выбор товаров
        ttk.Label(add_frame, text="Товар:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(add_frame, textvariable=self.product_var, state='readonly')
        self.product_combo.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(add_frame, text="Количество:").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_spin = ttk.Spinbox(add_frame, from_=1, to=100, textvariable=self.quantity_var, width=5)
        self.quantity_spin.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Button(add_frame, text="Добавить товар", command=self.add_product_to_order).grid(
            row=1, column=4, padx=5, pady=5)
        
        # Список товаров в заказе
        ttk.Label(add_frame, text="Товары в заказе:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.order_items_list = tk.Listbox(add_frame, height=5)
        self.order_items_list.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky='we')
        
        # Кнопка создания заказа
        ttk.Button(add_frame, text="Создать заказ", command=self.create_order).grid(
            row=3, column=0, columnspan=5, pady=10)
        
        # Список заказов
        list_frame = ttk.LabelFrame(frame, text="Список заказов")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ("id", "customer", "date", "status", "total")
        self.orders_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Определение заголовков
        self.orders_tree.heading("id", text="ID")
        self.orders_tree.heading("customer", text="Клиент")
        self.orders_tree.heading("date", text="Дата")
        self.orders_tree.heading("status", text="Статус")
        self.orders_tree.heading("total", text="Сумма")
        
        # Настройка столбцов
        self.orders_tree.column("id", width=50)
        self.orders_tree.column("customer", width=150)
        self.orders_tree.column("date", width=120)
        self.orders_tree.column("status", width=100)
        self.orders_tree.column("total", width=100)
        
        # Добавление scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.orders_tree.pack(side='left', fill='both', expand=True)
        
        # Кнопки управления
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="Обновить", command=self.update_orders_list).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Просмотреть детали", command=self.view_order_details).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Изменить статус", command=self.change_order_status).pack(side='left', padx=5)
        
        # Переменные для текущего заказа
        self.current_order_items = []
    
    def create_analysis_tab(self):
        """Создать вкладку для анализа данных."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Аналитика")
        
        # Кнопки для различных видов анализа
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Топ 5 клиентов", 
                  command=lambda: self.show_analysis("top_customers")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Динамика заказов", 
                  command=lambda: self.show_analysis("orders_dynamics")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Граф связей", 
                  command=lambda: self.show_analysis("customer_graph")).pack(side='left', padx=5)
        
        # Область для отображения графиков
        self.analysis_frame = ttk.Frame(frame)
        self.analysis_frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_import_export_tab(self):
        """Создать вкладку для импорта/экспорта данных."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Импорт/Экспорт")
        
        # Экспорт
        export_frame = ttk.LabelFrame(frame, text="Экспорт данных")
        export_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(export_frame, text="Таблица:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.export_table_var = tk.StringVar(value="customers")
        export_tables = ttk.Combobox(export_frame, textvariable=self.export_table_var, 
                                    values=["customers", "products", "orders"], state='readonly')
        export_tables.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(export_frame, text="Формат:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.export_format_var = tk.StringVar(value="CSV")
        export_format = ttk.Combobox(export_frame, textvariable=self.export_format_var, 
                                    values=["CSV", "JSON"], state='readonly')
        export_format.grid(row=0, column=3, padx=5, pady=5, sticky='we')
        
        ttk.Button(export_frame, text="Экспорт", command=self.export_data).grid(
            row=0, column=4, padx=5, pady=5)
        
        # Импорт
        import_frame = ttk.LabelFrame(frame, text="Импорт данных")
        import_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(import_frame, text="Таблица:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.import_table_var = tk.StringVar(value="customers")
        import_tables = ttk.Combobox(import_frame, textvariable=self.import_table_var, 
                                     values=["customers", "products", "orders"], state='readonly')
        import_tables.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(import_frame, text="Формат:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.import_format_var = tk.StringVar(value="CSV")
        import_format = ttk.Combobox(import_frame, textvariable=self.import_format_var, 
                                    values=["CSV", "JSON"], state='readonly')
        import_format.grid(row=0, column=3, padx=5, pady=5, sticky='we')
        
        ttk.Button(import_frame, text="Выбрать файл", command=self.import_data).grid(
            row=0, column=4, padx=5, pady=5)
    
    def add_customer(self):
        """Добавить нового клиента."""
        try:
            customer = Customer(
                id=0,  # ID будет присвоен базой данных
                first_name=self.first_name_entry.get(),
                last_name=self.last_name_entry.get(),
                email=self.email_entry.get(),
                phone=self.phone_entry.get(),
                address=self.address_entry.get()
            )
            
            customer_id = self.db.add_customer(customer)
            if customer_id != -1:
                messagebox.showinfo("Успех", f"Клиент добавлен с ID: {customer_id}")
                self.clear_customer_form()
                self.update_customers_list()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить клиента")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
    
    def add_product(self):
        """Добавить новый товар."""
        try:
            product = Product(
                id=0,  # ID будет присвоен базой данных
                name=self.product_name_entry.get(),
                price=float(self.product_price_entry.get()),
                category=self.product_category_entry.get()
            )
            
            product_id = self.db.add_product(product)
            if product_id != -1:
                messagebox.showinfo("Успех", f"Товар добавлен с ID: {product_id}")
                self.clear_product_form()
                self.update_products_list()
                self.update_product_combos()  # Обновить комбобоксы в заказах
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить товар")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
    
    def add_product_to_order(self):
        """Добавить товар в текущий заказ."""
        try:
            product_str = self.product_var.get()
            if not product_str:
                messagebox.showwarning("Предупреждение", "Выберите товар")
                return
            
            # Извлечь ID товара из строки (формат: "ID - Название")
            product_id = int(product_str.split(' - ')[0])
            quantity = int(self.quantity_var.get())
            
            # Найти товар в базе
            products = self.db.get_all_products()
            product = next((p for p in products if p.id == product_id), None)
            
            if product:
                # Добавить товар в текущий заказ
                self.current_order_items.append((product, quantity))
                
                # Обновить список товаров
                self.order_items_list.insert(tk.END, f"{product.name} - {quantity} шт. - {product.price * quantity} руб.")
                
                # Сбросить выбор товара
                self.product_var.set('')
                self.quantity_var.set('1')
            else:
                messagebox.showerror("Ошибка", "Товар не найден")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
    
    def create_order(self):
        """Создать новый заказ."""
        try:
            customer_str = self.customer_var.get()
            if not customer_str:
                messagebox.showwarning("Предупреждение", "Выберите клиента")
                return
            
            if not self.current_order_items:
                messagebox.showwarning("Предупреждение", "Добавьте товары в заказ")
                return
            
            # Извлечь ID клиента из строки (формат: "ID - Имя Фамилия")
            customer_id = int(customer_str.split(' - ')[0])
            
            # Создать заказ
            order = Order(
                id=0,  # ID будет присвоен базой данных
                customer_id=customer_id,
                order_date=datetime.now(),
                status="новый"
            )
            
            # Добавить товары в заказ
            for product, quantity in self.current_order_items:
                order.add_product(product, quantity)
            
            # Сохранить заказ в базе
            order_id = self.db.add_order(order)
            if order_id != -1:
                messagebox.showinfo("Успех", f"Заказ создан с ID: {order_id}")
                self.clear_order_form()
                self.update_orders_list()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать заказ")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
    
    def update_customers_list(self):
        """Обновить список клиентов."""
        # Очистить текущий список
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        # Загрузить клиентов из базы
        customers = self.db.get_all_customers()
        for customer in customers:
            self.customers_tree.insert('', 'end', values=(
                customer.id,
                customer.first_name,
                customer.last_name,
                customer.email,
                customer.phone,
                customer.address
            ))
        
        # Обновить комбобокс клиентов в заказах
        self.customer_combo['values'] = [f"{c.id} - {c.first_name} {c.last_name}" for c in customers]
    
    def update_products_list(self):
        """Обновить список товаров."""
        # Очистить текущий список
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Загрузить товары из базы
        products = self.db.get_all_products()
        for product in products:
            self.products_tree.insert('', 'end', values=(
                product.id,
                product.name,
                product.price,
                product.category
            ))
    
    def update_product_combos(self):
        """Обновить комбобоксы товаров в заказах."""
        products = self.db.get_all_products()
        self.product_combo['values'] = [f"{p.id} - {p.name}" for p in products]
    
    def update_orders_list(self):
        """Обновить список заказов."""
        # Очистить текущий список
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        # Загрузить заказы из базы
        orders = self.db.get_all_orders()
        customers = self.db.get_all_customers()
        
        for order in orders:
            # Найти клиента
            customer = next((c for c in customers if c.id == order.customer_id), None)
            customer_name = f"{customer.first_name} {customer.last_name}" if customer else "Неизвестный клиент"
            
            self.orders_tree.insert('', 'end', values=(
                order.id,
                customer_name,
                order.order_date.strftime("%Y-%m-%d %H:%M"),
                order.status,
                f"{order.total_cost():.2f}"
            ))
    
    def delete_customer(self):
        """Удалить выбранного клиента."""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите клиента для удаления")
            return
        
        customer_id = self.customers_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого клиента?"):
            # TODO: Реализовать удаление клиента из базы
            messagebox.showinfo("Информация", "Функция удаления будет реализована в следующей версии")
    
    def delete_product(self):
        """Удалить выбранный товар."""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар для удаления")
            return
        
        product_id = self.products_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот товар?"):
            # TODO: Реализовать удаление товара из базы
            messagebox.showinfo("Информация", "Функция удаления будет реализована в следующей версии")
    
    def search_customers(self):
        """Поиск клиентов по введенному запросу."""
        query = self.customer_search_entry.get().lower()
        if not query:
            self.update_customers_list()
            return
        
        # Очистить текущий список
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        # Загрузить клиентов из базы и отфильтровать
        customers = self.db.get_all_customers()
        for customer in customers:
            # Поиск по всем полям
            if (query in customer.first_name.lower() or 
                query in customer.last_name.lower() or 
                query in customer.email.lower() or 
                query in customer.phone.lower() or 
                query in customer.address.lower()):
                
                self.customers_tree.insert('', 'end', values=(
                    customer.id,
                    customer.first_name,
                    customer.last_name,
                    customer.email,
                    customer.phone,
                    customer.address
                ))
    
    def view_order_details(self):
        """Просмотреть детали выбранного заказа."""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите заказ для просмотра")
            return
        
        order_id = self.orders_tree.item(selection[0])['values'][0]
        
        # TODO: Реализовать просмотр деталей заказа
        messagebox.showinfo("Информация", "Функция просмотра деталей заказа будет реализована в следующей версии")
    
    def change_order_status(self):
        """Изменить статус выбранного заказа."""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите заказ для изменения статуса")
            return
        
        order_id = self.orders_tree.item(selection[0])['values'][0]
        
        # TODO: Реализовать изменение статуса заказа
        messagebox.showinfo("Информация", "Функция изменения статуса заказа будет реализована в следующей версии")
    
    def show_analysis(self, analysis_type):
        """Показать результаты анализа данных."""
        # Очистить область анализа
        for widget in self.analysis_frame.winfo_children():
            widget.destroy()
        
        try:
            if analysis_type == "top_customers":
                fig = self.analyzer.top_customers_by_orders()
            elif analysis_type == "orders_dynamics":
                fig = self.analyzer.orders_dynamics()
            elif analysis_type == "customer_graph":
                fig = self.analyzer.customer_connections_graph()
            else:
                return
            
            # Встроить график в интерфейс
            canvas = FigureCanvasTkAgg(fig, self.analysis_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить анализ: {e}")
    
    def export_data(self):
        """Экспортировать данные в выбранном формате."""
        table = self.export_table_var.get()
        format = self.export_format_var.get().lower()
        
        filename = filedialog.asksaveasfilename(
            defaultextension=f".{format}",
            filetypes=[(f"{format.upper()} files", f"*.{format}")]
        )
        
        if filename:
            try:
                if format == "csv":
                    self.db.export_to_csv(table, filename)
                elif format == "json":
                    self.db.export_to_json(table, filename)
                
                messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {e}")
    
    def import_data(self):
        """Импортировать данные из выбранного файла."""
        table = self.import_table_var.get()
        format = self.import_format_var.get().lower()
        
        filename = filedialog.askopenfilename(
            filetypes=[(f"{format.upper()} files", f"*.{format}")]
        )
        
        if filename:
            try:
                if format == "csv":
                    self.db.import_from_csv(table, filename)
                elif format == "json":
                    self.db.import_from_json(table, filename)
                
                messagebox.showinfo("Успех", f"Данные импортированы из {filename}")
                
                # Обновить списки
                self.update_customers_list()
                self.update_products_list()
                self.update_orders_list()
                self.update_product_combos()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать данные: {e}")
    
    def clear_customer_form(self):
        """Очистить форму добавления клиента."""
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
    
    def clear_product_form(self):
        """Очистить форму добавления товара."""
        self.product_name_entry.delete(0, tk.END)
        self.product_price_entry.delete(0, tk.END)
        self.product_category_entry.delete(0, tk.END)
    
    def clear_order_form(self):
        """Очистить форму создания заказа."""
        self.customer_var.set('')
        self.product_var.set('')
        self.quantity_var.set('1')
        self.order_items_list.delete(0, tk.END)
        self.current_order_items = []

def main():
    """Точка входа в приложение."""
    root = tk.Tk()
    app = ShopApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()