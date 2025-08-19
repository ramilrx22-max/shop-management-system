import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from datetime import datetime
from typing import List, Dict, Any, Optional
from db import Database
from models import Customer, Product, Order

class DataAnalyzer:
    """Класс для анализа и визуализации данных интернет-магазина.
    
    Attributes
    ----------
    db : Database
        Объект для работы с базой данных.
    """
    
    def __init__(self, db: Database):
        """Инициализация анализатора данных.
        
        Parameters
        ----------
        db : Database
            Объект для работы с базой данных.
        """
        self.db = db
        # Установка стиля для графиков
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def get_orders_dataframe(self) -> pd.DataFrame:
        """Получить данные о заказах в виде DataFrame.
        
        Returns
        -------
        pd.DataFrame
            DataFrame с данными о заказах.
        """
        orders = self.db.get_all_orders()
        customers = self.db.get_all_customers()
        products = self.db.get_all_products()
        
        # Создаем словарь для быстрого доступа к данным клиентов и товаров
        customer_dict = {c.id: f"{c.first_name} {c.last_name}" for c in customers}
        product_dict = {p.id: p.name for p in products}
        
        # Подготавливаем данные для DataFrame
        data = []
        for order in orders:
            for product, quantity in order.items:
                data.append({
                    'order_id': order.id,
                    'customer_id': order.customer_id,
                    'customer_name': customer_dict.get(order.customer_id, 'Неизвестный'),
                    'order_date': order.order_date,
                    'status': order.status,
                    'product_id': product.id,
                    'product_name': product_dict.get(product.id, 'Неизвестный товар'),
                    'quantity': quantity,
                    'price': product.price,
                    'total': product.price * quantity
                })
        
        return pd.DataFrame(data)
    
    def get_customers_dataframe(self) -> pd.DataFrame:
        """Получить данные о клиентах в виде DataFrame.
        
        Returns
        -------
        pd.DataFrame
            DataFrame с данными о клиентах.
        """
        customers = self.db.get_all_customers()
        
        data = []
        for customer in customers:
            data.append({
                'customer_id': customer.id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'email': customer.email,
                'phone': customer.phone,
                'address': customer.address
            })
        
        return pd.DataFrame(data)
    
    def top_customers_by_orders(self, top_n: int = 5) -> plt.Figure:
        """Визуализировать топ-N клиентов по количеству заказов.
        
        Parameters
        ----------
        top_n : int, optional
            Количество клиентов для отображения. По умолчанию 5.
            
        Returns
        -------
        plt.Figure
            Объект рисунка с графиком.
        """
        df = self.get_orders_dataframe()
        
        if df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Нет данных для отображения', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            return fig
        
        # Группируем по клиентам и считаем количество уникальных заказов
        customer_orders = df.groupby('customer_name')['order_id'].nunique().sort_values(ascending=False).head(top_n)
        
        # Создаем график
        fig, ax = plt.subplots(figsize=(10, 6))
        customer_orders.plot(kind='bar', ax=ax, color=sns.color_palette("husl", len(customer_orders)))
        
        ax.set_title(f'Топ {top_n} клиентов по количеству заказов', fontsize=16, fontweight='bold')
        ax.set_xlabel('Клиент', fontsize=12)
        ax.set_ylabel('Количество заказов', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        
        # Добавляем значения на столбцы
        for i, v in enumerate(customer_orders):
            ax.text(i, v + 0.1, str(v), ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def orders_dynamics(self, period: str = 'D') -> plt.Figure:
        """Визуализировать динамику количества заказов по датам.
        
        Parameters
        ----------
        period : str, optional
            Период агрегации данных. По умолчанию 'D' (дни).
            Другие варианты: 'W' (недели), 'M' (месяцы).
            
        Returns
        -------
        plt.Figure
            Объект рисунка с графиком.
        """
        df = self.get_orders_dataframe()
        
        if df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Нет данных для отображения', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            return fig
        
        # Убираем дубликаты заказов (так как в DataFrame каждый товар в заказе - отдельная строка)
        unique_orders = df.drop_duplicates('order_id')
        
        # Группируем по дате и считаем количество заказов
        orders_by_date = unique_orders.set_index('order_date').resample(period).size()
        
        # Создаем график
        fig, ax = plt.subplots(figsize=(12, 6))
        orders_by_date.plot(ax=ax, marker='o', linewidth=2)
        
        # Настраиваем заголовки и метки
        if period == 'D':
            period_name = 'дням'
        elif period == 'W':
            period_name = 'неделям'
        elif period == 'M':
            period_name = 'месяцам'
        else:
            period_name = 'периодам'
            
        ax.set_title(f'Динамика количества заказов по {period_name}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Дата', fontsize=12)
        ax.set_ylabel('Количество заказов', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def customer_connections_graph(self, min_common_products: int = 2) -> plt.Figure:
        """Построить граф связей клиентов по общим товарам.
        
        Parameters
        ----------
        min_common_products : int, optional
            Минимальное количество общих товаров для создания связи.
            По умолчанию 2.
            
        Returns
        -------
        plt.Figure
            Объект рисунка с графом.
        """
        df = self.get_orders_dataframe()
        
        if df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Нет данных для отображения', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            return fig
        
        # Создаем словарь: клиент -> набор купленных товаров
        customer_products = {}
        for customer_id in df['customer_id'].unique():
            customer_products[customer_id] = set(df[df['customer_id'] == customer_id]['product_id'].unique())
        
        # Создаем граф
        G = nx.Graph()
        
        # Добавляем узлы (клиенты)
        for customer_id, products in customer_products.items():
            customer_name = df[df['customer_id'] == customer_id]['customer_name'].iloc[0]
            G.add_node(customer_id, label=customer_name, size=len(products))
        
        # Добавляем ребра между клиентами с общими товарами
        customers = list(customer_products.keys())
        for i in range(len(customers)):
            for j in range(i + 1, len(customers)):
                common_products = customer_products[customers[i]] & customer_products[customers[j]]
                if len(common_products) >= min_common_products:
                    G.add_edge(customers[i], customers[j], weight=len(common_products))
        
        # Визуализируем граф
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Если в графе нет ребер, отображаем сообщение
        if len(G.edges) == 0:
            ax.text(0.5, 0.5, 'Недостаточно данных для построения графа связей', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            return fig
        
        # Позиционирование узлов
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Размер узлов пропорционален количеству купленных товаров
        node_sizes = [G.nodes[node]['size'] * 100 for node in G.nodes()]
        
        # Рисуем узлы
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, 
                              node_color='lightblue', alpha=0.7, ax=ax)
        
        # Рисуем ребра с толщиной, пропорциональной весу (количеству общих товаров)
        edge_widths = [G[u][v]['weight'] for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos, width=edge_widths, 
                              alpha=0.5, edge_color='gray', ax=ax)
        
        # Добавляем подписи узлов
        labels = {node: G.nodes[node]['label'] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=10, ax=ax)
        
        # Добавляем подписи ребер (вес - количество общих товаров)
        edge_labels = {(u, v): G[u][v]['weight'] for u, v in G.edges()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, ax=ax)
        
        ax.set_title('Граф связей клиентов по общим товарам', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        return fig
    
    def sales_by_category(self) -> plt.Figure:
        """Визуализировать продажи по категориям товаров.
        
        Returns
        -------
        plt.Figure
            Объект рисунка с графиком.
        """
        df = self.get_orders_dataframe()
        
        if df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Нет данных для отображения', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            return fig
        
        # Группируем по категориям и суммируем продажи
        sales_by_category = df.groupby('product_name')['total'].sum().sort_values(ascending=False)
        
        # Создаем круговую диаграмму
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Если категорий слишком много, показываем только топ-10
        if len(sales_by_category) > 10:
            top_categories = sales_by_category.head(10)
            other_sales = sales_by_category[10:].sum()
            top_categories['Другие'] = other_sales
            sales_data = top_categories
        else:
            sales_data = sales_by_category
        
        wedges, texts, autotexts = ax.pie(sales_data.values, labels=sales_data.index, autopct='%1.1f%%',
                                          startangle=90, colors=sns.color_palette("husl", len(sales_data)))
        
        ax.set_title('Распределение продаж по товарам', fontsize=16, fontweight='bold')
        
        # Улучшаем читаемость подписей
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        return fig
    
    def customer_geography(self) -> plt.Figure:
        """Визуализировать географическое распределение клиентов.
        
        Returns
        -------
        plt.Figure
            Объект рисунка с картой клиентов.
        """
        df = self.get_customers_dataframe()
        
        if df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Нет данных для отображения', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            return fig
        
        # Извлекаем города из адресов (простая эвристика)
        df['city'] = df['address'].apply(lambda x: x.split(',')[0].strip() if ',' in x else x.strip())
        
        # Группируем по городам
        customers_by_city = df['city'].value_counts()
        
        # Создаем график
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Если городов слишком много, показываем только топ-15
        if len(customers_by_city) > 15:
            top_cities = customers_by_city.head(15)
        else:
            top_cities = customers_by_city
        
        top_cities.plot(kind='bar', ax=ax, color=sns.color_palette("husl", len(top_cities)))
        
        ax.set_title('Географическое распределение клиентов', fontsize=16, fontweight='bold')
        ax.set_xlabel('Город', fontsize=12)
        ax.set_ylabel('Количество клиентов', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        
        # Добавляем значения на столбцы
        for i, v in enumerate(top_cities):
            ax.text(i, v + 0.1, str(v), ha='center', va='bottom')
        
        plt.tight_layout()
        return fig

# Пример использования
if __name__ == "__main__":
    # Создаем подключение к базе данных
    db = Database()
    
    # Создаем анализатор
    analyzer = DataAnalyzer(db)
    
    # Строим графики
    fig1 = analyzer.top_customers_by_orders()
    fig2 = analyzer.orders_dynamics('W')
    fig3 = analyzer.customer_connections_graph()
    fig4 = analyzer.sales_by_category()
    fig5 = analyzer.customer_geography()
    
    # Показываем графики
    plt.show()
    
    # Закрываем подключение к базе данных
    db.close()