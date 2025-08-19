# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

# Добавляем путь к проекту, чтобы Sphinx мог найти ваши модули
sys.path.insert(0, os.path.abspath('../../'))

project = 'Order Managment System'
copyright = '2025, Ramil Khusnutdinov'
author = 'Ramil Khusnutdinov'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Добавляем необходимые расширения
extensions = [
    'sphinx.ext.autodoc',    # Для автоматического извлечения документации из docstrings
    'sphinx.ext.viewcode',   # Добавляет ссылки на исходный код
    'sphinx.ext.napoleon'    # Поддержка Google и NumPy стиля docstrings
]

templates_path = ['_templates']
exclude_patterns = []

language = 'ru'

# Указываем, какие модули нужно "мокировать" (эмулировать) при построении документации
# Это необходимо для модулей, которые могут отсутствовать в среде построения документации
autodoc_mock_imports = ['tkinter', 'pandas', 'matplotlib', 'seaborn', 'networkx', 'sqlite3']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

# Подавление определенных предупреждений
suppress_warnings = [
    'autodoc', 
    'app.add_directive',
    'app.add_node'
]

# Игнорировать модули, которые не нужно документировать
autodoc_mock_imports = ['tkinter', 'pandas', 'matplotlib', 'seaborn', 'networkx', 'sqlite3']

# Не документировать тестовые модули
exclude_patterns = ['test_*.py']

# Полное отключение предупреждений
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='sphinx')