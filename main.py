#!/usr/bin/env python3
"""
Главный модуль приложения для управления интернет-магазином.
Точка входа в программу.
"""

import tkinter as tk
from gui import ShopApp

def main():
    """Основная функция для запуска приложения."""
    root = tk.Tk()
    app = ShopApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()