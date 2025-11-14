import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QCalendarWidget,
    QPushButton,
    QMessageBox,
    QDialog,
)

from add_recipe_dialog import AddRecipeDialog
from recipe_library import RecipeLibraryWindow
from planner_dialog import PlannerDialog
from shopping_list_window import ShoppingListWindow
import database


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Менеджер книги рецептов")
        self.setGeometry(100, 100, 450, 450)

        database.init_db()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.calendar = QCalendarWidget()
        self.calendar.selectionChanged.connect(self.calendar_date_selected)
        layout.addWidget(self.calendar)

        self.add_recipe_btn = QPushButton("1. Добавить новый рецепт")
        self.add_recipe_btn.clicked.connect(self.open_add_recipe_dialog)
        layout.addWidget(self.add_recipe_btn)

        self.library_btn = QPushButton("2. Открыть библиотеку")
        self.library_btn.clicked.connect(self.open_library_window)
        layout.addWidget(self.library_btn)

        self.shopping_list_btn = QPushButton("3. Сгенерировать список покупок")
        self.shopping_list_btn.clicked.connect(self.open_shopping_list_window)
        layout.addWidget(self.shopping_list_btn)

    def calendar_date_selected(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        dialog = PlannerDialog(selected_date, self)
        dialog.exec()

    def open_add_recipe_dialog(self):
        dialog = AddRecipeDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, instructions, image_path, ingredients_str = dialog.get_data()
            if name and instructions:
                self.save_recipe_to_db(name, instructions, image_path, ingredients_str)
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Название и инструкции не могут быть пустыми!"
                )

    def save_recipe_to_db(self, name, instructions, image_path, ingredients_str):
        try:
            conn = sqlite3.connect("recipe_book.db")
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO Recipes (name, instructions, image_path) VALUES (?, ?, ?)",
                (name, instructions, image_path),
            )
            recipe_id = cursor.lastrowid

            ingredients_list = [
                i.strip() for i in ingredients_str.split(",") if i.strip()
            ]

            for item in ingredients_list:
                start_paren = item.rfind("(")
                end_paren = item.rfind(")")

                ing_name = item.strip()
                quantity = ""

                if start_paren != -1 and end_paren == len(item) - 1:
                    ing_name = item[:start_paren].strip()
                    quantity = item[start_paren + 1 : end_paren].strip()

                if not ing_name:
                    continue

                cursor.execute(
                    "INSERT OR IGNORE INTO Ingredients (name) VALUES (?)", (ing_name,)
                )
                cursor.execute("SELECT id FROM Ingredients WHERE name=?", (ing_name,))
                ing_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO Recipe_Ingredients (recipe_id, ingredient_id, quantity) VALUES (?, ?, ?)",
                    (recipe_id, ing_id, quantity),
                )

            conn.commit()
            QMessageBox.information(self, "Успех", f"Рецепт '{name}' сохранен")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось сохранить рецепт: {e}")
        finally:
            if conn:
                conn.close()

    def open_library_window(self):
        self.library_window = RecipeLibraryWindow(self)
        self.library_window.show()

    def open_shopping_list_window(self):
        self.shopping_list_window = ShoppingListWindow(self)
        self.shopping_list_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
