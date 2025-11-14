from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QMessageBox,
    QFileDialog,
    QDateEdit,
    QHBoxLayout,
    QLabel,
)
from PyQt6.QtCore import QDate
import sqlite3
import collections


class ShoppingListWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Генератор Списка Покупок")
        self.setGeometry(400, 400, 500, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        date_layout = QHBoxLayout()
        self.date_start = QDateEdit(QDate.currentDate())
        self.date_end = QDateEdit(QDate.currentDate().addDays(6))
        date_layout.addWidget(QLabel("С даты:"))
        date_layout.addWidget(self.date_start)
        date_layout.addWidget(QLabel("По дату:"))
        date_layout.addWidget(self.date_end)
        main_layout.addLayout(date_layout)

        self.generate_btn = QPushButton("Сгенерировать")
        self.generate_btn.clicked.connect(self.generate_list)
        main_layout.addWidget(self.generate_btn)

        self.export_btn = QPushButton("Экспорт в TXT")
        self.export_btn.clicked.connect(self.export_to_txt)
        main_layout.addWidget(self.export_btn)

        self.list_view = QTextEdit()
        self.list_view.setReadOnly(True)
        main_layout.addWidget(self.list_view)

        self.shopping_list_data = ""

    def generate_list(self):
        start_date = self.date_start.date().toString("yyyy-MM-dd")
        end_date = self.date_end.date().toString("yyyy-MM-dd")

        ingredients_map = collections.defaultdict(list)

        try:
            conn = sqlite3.connect("recipe_book.db")
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT T1.recipe_id FROM Meal_Plan T1 
                WHERE T1.date BETWEEN ? AND ?
            """,
                (start_date, end_date),
            )

            recipe_ids = set([row[0] for row in cursor.fetchall()])

            if not recipe_ids:
                self.list_view.setText("На выбранный период блюда не запланированы")
                self.shopping_list_data = ""
                return

            for recipe_id in recipe_ids:
                cursor.execute(
                    """
                    SELECT T2.name, T3.quantity FROM Recipes T1
                    JOIN Recipe_Ingredients T3 ON T1.id = T3.recipe_id
                    JOIN Ingredients T2 ON T3.ingredient_id = T2.id
                    WHERE T1.id = ?
                """,
                    (recipe_id,),
                )

                for ing_name, quantity in cursor.fetchall():
                    ingredients_map[ing_name].append(
                        quantity if quantity else "не указано"
                    )

            conn.close()

            output = f"СПИСОК ПОКУПОК ({start_date} - {end_date})\n\n"
            for name, quantities in ingredients_map.items():
                qty_str = ", ".join(quantities)
                output += f"- {name}: {qty_str}\n"

            self.list_view.setText(output)
            self.shopping_list_data = output

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка генерации списка: {e}")

    def export_to_txt(self):
        if not self.shopping_list_data:
            QMessageBox.warning(
                self, "Предупреждение", "Сначала сгенерируйте список покупок"
            )
            return

        fname, _ = QFileDialog.getSaveFileName(
            self, "Сохранить список покупок", "shopping_list.txt", "Text Files (*.txt)"
        )

        if fname:
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(self.shopping_list_data)
                QMessageBox.information(
                    self, "Успех", f"Список успешно сохранен в: {fname}"
                )
            except IOError as e:
                QMessageBox.critical(
                    self, "Ошибка файла", f"Не удалось сохранить файл: {e}"
                )
