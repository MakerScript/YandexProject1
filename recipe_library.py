from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QHeaderView,
    QDialog,
)
from PyQt6.QtCore import Qt
import sqlite3
from add_recipe_dialog import AddRecipeDialog


class RecipeLibraryWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Библиотека Рецептов")
        self.setGeometry(200, 200, 800, 500)
        self.setStyleSheet("font-size: 10pt;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Инструкции"])
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.setColumnHidden(0, True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        self.edit_btn = QPushButton("Редактировать выбранный рецепт")
        self.edit_btn.clicked.connect(self.edit_selected_recipe)
        layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Удалить выбранный рецепт")
        self.delete_btn.clicked.connect(self.delete_selected_recipe)
        layout.addWidget(self.delete_btn)

        self.load_recipes()

    def load_recipes(self):
        self.table.setRowCount(0)
        try:
            conn = sqlite3.connect("recipe_book.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, instructions, image_path FROM Recipes")
            recipes = cursor.fetchall()
            conn.close()

            self.table.setRowCount(len(recipes))
            for row_idx, recipe in enumerate(recipes):
                for col_idx, data in enumerate(recipe[:3]):
                    item = QTableWidgetItem(str(data))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row_idx, col_idx, item)

        except sqlite3.Error as e:
            QMessageBox.critical(
                self, "Ошибка БД", f"Не удалось загрузить рецепты: {e}"
            )

    def get_selected_recipe_data(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None

        row = selected_rows[0].row()
        recipe_id = int(self.table.item(row, 0).text())

        try:
            conn = sqlite3.connect("recipe_book.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, instructions, image_path FROM Recipes WHERE id=?",
                (recipe_id,),
            )
            data = cursor.fetchone()
            conn.close()
            return data
        except sqlite3.Error as e:
            QMessageBox.critical(
                self, "Ошибка БД", f"Не удалось получить данные для редактирования: {e}"
            )
            return None

    def edit_selected_recipe(self):
        data = self.get_selected_recipe_data()
        if not data:
            QMessageBox.warning(
                self, "Предупреждение", "Выберите рецепт для редактирования"
            )
            return

        dialog = AddRecipeDialog(self, recipe_data=data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, instructions, image_path, ingredients_str = dialog.get_data()
            if name and instructions:
                self.update_recipe_in_db(
                    data[0], name, instructions, image_path, ingredients_str
                )
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Название и инструкции не могут быть пустыми!"
                )

    def update_recipe_in_db(
        self, recipe_id, name, instructions, image_path, ingredients_str
    ):
        try:
            conn = sqlite3.connect("recipe_book.db")
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE Recipes SET name=?, instructions=?, image_path=? WHERE id=?
            """,
                (name, instructions, image_path, recipe_id),
            )

            cursor.execute(
                "DELETE FROM Recipe_Ingredients WHERE recipe_id=?", (recipe_id,)
            )

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
            conn.close()
            QMessageBox.information(self, "Успех", f"Рецепт '{name}' успешно обновлен")
            self.load_recipes()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось обновить рецепт: {e}")

    def delete_selected_recipe(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите рецепт для удаления")
            return

        recipe_id = self.table.item(selected_rows[0].row(), 0).text()
        recipe_name = self.table.item(selected_rows[0].row(), 1).text()

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить рецепт '{recipe_name}'? Это действие нельзя отменить",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect("recipe_book.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Recipes WHERE id = ?", (recipe_id,))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Успех", f"Рецепт '{recipe_name}' удален")
                self.load_recipes()
            except sqlite3.Error as e:
                QMessageBox.critical(
                    self, "Ошибка БД", f"Не удалось удалить рецепт: {e}"
                )
