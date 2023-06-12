import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QDialog, QCalendarWidget, QListWidget, QListWidgetItem
from PyQt5.QtCore import QDate, Qt
import sqlite3
import re
import datetime

# Создаем подключение к базе данных
conn = sqlite3.connect('lombard.db')
cursor = conn.cursor()

# Создаем таблицу для хранения данных клиентов
cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        last_name TEXT,
        first_name TEXT,
        patronymic TEXT,
        phone TEXT
    )
''')

# Создаем таблицу для хранения данных оценки товара
cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        estimated_value REAL,
        return_date TEXT
    )
''')

# Создаем таблицу для хранения цен на товары
cursor.execute('''
    CREATE TABLE IF NOT EXISTS item_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT,
        price REAL
    )
''')

# Создаем графическое окно
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ломбард")
        self.layout = QVBoxLayout()

        # Создаем поля для ввода данных клиента
        self.last_name_label = QLabel("Фамилия:")
        self.last_name_input = QLineEdit()

        self.first_name_label = QLabel("Имя:")
        self.first_name_input = QLineEdit()

        self.patronymic_label = QLabel("Отчество:")
        self.patronymic_input = QLineEdit()

        self.phone_label = QLabel("Телефон:")
        self.phone_input = QLineEdit()

        # Кнопка для регистрации клиента
        self.register_button = QPushButton("Зарегистрировать")
        self.register_button.clicked.connect(self.register_client)

        # Кнопка для оценки стоимости товара
        self.estimate_button = QPushButton("Оценить товар")
        self.estimate_button.clicked.connect(self.estimate_item)

        # Кнопка для изменения цены товара
        self.update_price_button = QPushButton("Изменить цену товара")
        self.update_price_button.clicked.connect(self.update_item_price)

        # Кнопка для расчета суммы займа и комиссионных
        self.calculate_button = QPushButton("Рассчитать займ и комиссионные")
        self.calculate_button.clicked.connect(self.calculate_loan)

        # Кнопка для оформления договора
        self.contract_button = QPushButton("Оформить договор")
        self.contract_button.clicked.connect(self.generate_contract)

        # Кнопка для выдачи денег и хранения товара
        self.issue_button = QPushButton("Выдать деньги и хранить товар")
        self.issue_button.clicked.connect(self.issue_money)

        # Кнопка для возврата денег
        self.return_button = QPushButton("Вернуть деньги")
        self.return_button.clicked.connect(self.return_money)

        # Кнопка для получения информации о товаре
        self.item_info_button = QPushButton("Информация о товаре")
        self.item_info_button.clicked.connect(self.get_item_info)

        # Кнопка для поиска
        self.search_button = QPushButton("Поиск")
        self.search_button.clicked.connect(self.search)

        self.layout.addWidget(self.last_name_label)
        self.layout.addWidget(self.last_name_input)
        self.layout.addWidget(self.first_name_label)
        self.layout.addWidget(self.first_name_input)
        self.layout.addWidget(self.patronymic_label)
        self.layout.addWidget(self.patronymic_input)
        self.layout.addWidget(self.phone_label)
        self.layout.addWidget(self.phone_input)
        self.layout.addWidget(self.register_button)
        self.layout.addWidget(self.estimate_button)
        self.layout.addWidget(self.update_price_button)
        self.layout.addWidget(self.calculate_button)
        self.layout.addWidget(self.contract_button)
        self.layout.addWidget(self.issue_button)
        self.layout.addWidget(self.return_button)
        self.layout.addWidget(self.item_info_button)
        self.layout.addWidget(self.search_button)

        self.setLayout(self.layout)

        # Переменные для хранения данных о клиенте и товаре
        self.client_id = None
        self.item_id = None

    def register_client(self):
        last_name = self.last_name_input.text().strip()
        first_name = self.first_name_input.text().strip()
        patronymic = self.patronymic_input.text().strip()
        phone = self.phone_input.text().strip()

        # Проверяем, что все поля заполнены
        if last_name and first_name and patronymic and phone:
            # Проверяем корректность ввода Фамилии, Имени и Отчества
            name_pattern = re.compile(r'^[А-ЯЁ][а-яё]*$')
            if not name_pattern.match(last_name) or not name_pattern.match(first_name) or not name_pattern.match(patronymic):
                QMessageBox.warning(self, "Ошибка", "Некорректное заполнение полей Фамилия, Имя или Отчество!")
                return

            # Проверяем корректность ввода номера телефона
            phone_pattern = re.compile(r'^\d{11}$')
            if not phone_pattern.match(phone):
                QMessageBox.warning(self, "Ошибка", "Некорректный номер телефона! Введите 11 цифр без пробелов и разделителей.")
                return

            # Вставляем данные клиента в таблицу
            cursor.execute("INSERT INTO clients (last_name, first_name, patronymic, phone) VALUES (?, ?, ?, ?)",
                           (last_name, first_name, patronymic, phone))
            conn.commit()

            # Получаем ID сохраненного клиента
            self.client_id = cursor.lastrowid

            # Очищаем поля ввода
            self.last_name_input.clear()
            self.first_name_input.clear()
            self.patronymic_input.clear()
            self.phone_input.clear()

            # Выводим сообщение об успешной регистрации
            QMessageBox.information(self, "Регистрация", "Клиент успешно зарегистрирован!")
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля!")

    def estimate_item(self):
        if self.client_id is None:
            QMessageBox.warning(self, "Ошибка", "Сначала зарегистрируйте клиента!")
            return

        dialog = QDialog()
        dialog.setWindowTitle("Оценка товара")
        dialog.layout = QVBoxLayout()

        item_name_label = QLabel("Наименование:")
        item_name_input = QLineEdit()

        item_description_label = QLabel("Описание:")
        item_description_input = QLineEdit()

        item_value_label = QLabel("Оценочная стоимость:")
        item_value_input = QLineEdit()

        return_date_label = QLabel("Срок возврата:")
        calendar_widget = QCalendarWidget()
        calendar_widget.setMinimumDate(QDate.currentDate())

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(
            lambda: self.save_item(dialog, item_name_input.text(), item_description_input.text(),
                                   item_value_input.text(), calendar_widget.selectedDate()))

        dialog.item_name_input = item_name_input
        dialog.item_description_input = item_description_input
        dialog.item_value_input = item_value_input

        dialog.layout.addWidget(item_name_label)
        dialog.layout.addWidget(item_name_input)
        dialog.layout.addWidget(item_description_label)
        dialog.layout.addWidget(item_description_input)
        dialog.layout.addWidget(item_value_label)
        dialog.layout.addWidget(item_value_input)
        dialog.layout.addWidget(return_date_label)
        dialog.layout.addWidget(calendar_widget)
        dialog.layout.addWidget(save_button)

        dialog.setLayout(dialog.layout)
        dialog.exec_()

    def save_item(self, dialog, name, description, value, return_date):
        if name and description and value and return_date:
            value_pattern = re.compile(r'^\d+(\.\d+)?$')
            if not value_pattern.match(value):
                QMessageBox.warning(dialog, "Ошибка", "Некорректная оценочная стоимость! Введите число или десятичную дробь.")
                return

            selected_date = return_date.toPyDate()
            current_date = QDate.currentDate().toPyDate()
            if selected_date < current_date:
                QMessageBox.warning(dialog, "Ошибка", "Некорректная дата! Выберите дату, которая больше или равна текущей дате.")
                return

            # Вставляем данные о товаре в таблицу
            cursor.execute("INSERT INTO items (name, description, estimated_value, return_date) VALUES (?, ?, ?, ?)",
                           (name, description, float(value), selected_date.isoformat()))
            conn.commit()

            self.item_id = cursor.lastrowid

            dialog.item_name_input.clear()
            dialog.item_description_input.clear()
            dialog.item_value_input.clear()

            dialog.accept()

            QMessageBox.information(self, "Оценка товара", "Товар успешно оценен!")
        else:
            QMessageBox.warning(dialog, "Ошибка", "Пожалуйста, заполните все поля!")

    def update_item_price(self):
        if self.item_id is None:
            QMessageBox.warning(self, "Ошибка", "Сначала оцените товар!")
            return

        dialog = QDialog()
        dialog.setWindowTitle("Изменение цены товара")
        dialog.layout = QVBoxLayout()

        item_price_label = QLabel("Цена:")
        item_price_input = QLineEdit()

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(
            lambda: self.save_item_price(dialog, item_price_input.text()))

        dialog.item_price_input = item_price_input

        dialog.layout.addWidget(item_price_label)
        dialog.layout.addWidget(item_price_input)
        dialog.layout.addWidget(save_button)

        dialog.setLayout(dialog.layout)
        dialog.exec_()

    def save_item_price(self, dialog, price):
        if price:
            value_pattern = re.compile(r'^\d+(\.\d+)?$')
            if not value_pattern.match(price):
                QMessageBox.warning(dialog, "Ошибка", "Некорректная цена! Введите число или десятичную дробь.")
                return

            # Вставляем цену товара в таблицу item_prices
            cursor.execute("INSERT INTO item_prices (item_name, price) VALUES (?, ?)",
                           (self.item_id, float(price)))
            conn.commit()

            dialog.item_price_input.clear()

            dialog.accept()

            QMessageBox.information(self, "Изменение цены товара", "Цена товара успешно изменена!")
        else:
            QMessageBox.warning(dialog, "Ошибка", "Пожалуйста, введите цену!")

    def calculate_loan(self):
        if self.client_id is None:
            QMessageBox.warning(self, "Ошибка", "Сначала зарегистрируйте клиента!")
            return

        if self.item_id is None:
            QMessageBox.warning(self, "Ошибка", "Сначала оцените товар!")
            return

        cursor.execute("SELECT estimated_value FROM items WHERE id=?", (self.item_id,))
        estimated_value = cursor.fetchone()[0]

        loan_amount = estimated_value * 0.8
        commission = estimated_value * 0.05

        loan_amount = round(loan_amount, 2)
        commission = round(commission, 2)

        QMessageBox.information(self, "Расчет", f"Оценочная стоимость товара: {estimated_value}\nСумма займа: {loan_amount}\nКомиссионные: {commission}")

    def generate_contract(self):
        if self.client_id is None:
            QMessageBox.warning(self, "Ошибка", "Сначала зарегистрируйте клиента!")
            return

        if self.item_id is None:
            QMessageBox.warning(self, "Ошибка", "Сначала оцените товар!")
            return

        cursor.execute("SELECT last_name, first_name, patronymic, phone FROM clients WHERE id=?", (self.client_id,))
        client_data = cursor.fetchone()
        last_name, first_name, patronymic, phone = client_data

        cursor.execute("SELECT name, description, estimated_value, return_date FROM items WHERE id=?", (self.item_id,))
        item_data = cursor.fetchone()
        item_name, item_description, item_value, return_date = item_data

        # Генерация текста договора
        contract_text = f"ДОГОВОР ЗАЙМА И ЗАЛОГА\n\nКлиент:\nФамилия: {last_name}\nИмя: {first_name}\nОтчество: {patronymic}\nТелефон: {phone}\n\n"
        contract_text += f"Товар:\nНаименование: {item_name}\nОписание: {item_description}\nОценочная стоимость: {item_value}\nСрок возврата: {return_date.toString('dd.MM.yyyy')}\n\n"
        # Добавьте остальные необходимые данные договора

        filename = f"{last_name}.doc"
        with open(filename, "w") as file:
            file.write(contract_text)

        QMessageBox.information(self, "Оформление договора", f"Договор успешно оформлен и сохранен в файле {filename}!")

    def issue_money(self):
        if self.client_id is None:
            QMessageBox.warning(self, "Ошибка", "Сначала зарегистрируйте клиента!")
            return

        if self.item_id is None:
            QMessageBox.warning(self, "Ошибка", "Сначала оцените товар!")
            return

        QMessageBox.information(self, "Выдача денег", "Деньги выданы клиенту, товар оставлен в ломбарде под залог.")

    def return_money(self):
        # Создаем окно для выбора клиента
        dialog = QDialog()
        dialog.setWindowTitle("Выбор клиента")
        dialog.layout = QVBoxLayout()

        client_list = QListWidget()
        self.populate_client_list(client_list)

        return_button = QPushButton("Вернуть деньги")
        return_button.clicked.connect(lambda: self.process_return(dialog, client_list))

        dialog.layout.addWidget(client_list)
        dialog.layout.addWidget(return_button)
        dialog.setLayout(dialog.layout)
        dialog.exec_()

    def populate_client_list(self, list_widget):
        list_widget.clear()

        # Получаем данные всех клиентов из базы данных
        cursor.execute("SELECT id, last_name, first_name, patronymic FROM clients")
        clients = cursor.fetchall()

        # Добавляем клиентов в список
        for client in clients:
            client_id, last_name, first_name, patronymic = client
            item = QListWidgetItem(f"{last_name} {first_name} {patronymic}")
            item.setData(Qt.UserRole, client_id)
            list_widget.addItem(item)

    def process_return(self, dialog, client_list):
        selected_item = client_list.currentItem()
        if selected_item:
            client_id = selected_item.data(Qt.UserRole)

            # Возвращаем деньги клиенту
            cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
            conn.commit()

            # Обновляем список клиентов
            self.populate_client_list(client_list)

            QMessageBox.information(self, "Возврат денег", "Деньги возвращены клиенту.")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента из списка.")

    def get_item_info(self):
        if self.item_id is None:
            QMessageBox.warning(self, "Ошибка", "Сначала оцените товар!")
            return

        cursor.execute("SELECT name, description, estimated_value, return_date FROM items WHERE id=?", (self.item_id,))
        item_data = cursor.fetchone()
        item_name, item_description, item_value, return_date = item_data

        info_text = f"Информация о товаре:\n\n"
        info_text += f"Наименование: {item_name}\nОписание: {item_description}\nОценочная стоимость: {item_value}\nСрок возврата: {return_date}\n"

        QMessageBox.information(self, "Информация о товаре", info_text)

    def search(self):
        dialog = QDialog()
        dialog.setWindowTitle("Поиск")
        dialog.layout = QVBoxLayout()

        search_label = QLabel("Поиск:")
        search_input = QLineEdit()

        search_button = QPushButton("Найти")
        search_button.clicked.connect(lambda: self.perform_search(dialog, search_input.text()))

        dialog.layout.addWidget(search_label)
        dialog.layout.addWidget(search_input)
        dialog.layout.addWidget(search_button)

        dialog.setLayout(dialog.layout)
        dialog.exec_()

    def perform_search(self, dialog, query):
        if query:
            # Поиск клиентов по фамилии или имени
            cursor.execute("SELECT * FROM clients WHERE last_name LIKE ? OR first_name LIKE ?",
                           (f"%{query}%", f"%{query}%"))
            clients = cursor.fetchall()

            # Поиск товара по наименованию
            cursor.execute("SELECT * FROM items WHERE name LIKE ?", (f"%{query}%",))
            items = cursor.fetchall()

            result_text = ""

            if clients:
                result_text += "Найденные клиенты:\n"
                for client in clients:
                    result_text += f"ID: {client[0]}, Фамилия: {client[1]}, Имя: {client[2]}, Отчество: {client[3]}, Телефон: {client[4]}\n"
                result_text += "\n"

            if items:
                result_text += "Найденные товары:\n"
                for item in items:
                    result_text += f"ID: {item[0]}, Наименование: {item[1]}, Описание: {item[2]}, Оценочная стоимость: {item[3]}, Срок возврата: {item[4]}\n"
                result_text += "\n"

            if result_text:
                QMessageBox.information(self, "Поиск", result_text)
            else:
                QMessageBox.information(self, "Поиск", "По вашему запросу ничего не найдено.")
        else:
            QMessageBox.warning(dialog, "Ошибка", "Пожалуйста, введите поисковый запрос!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
