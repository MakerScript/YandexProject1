from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
    QComboBox,
    QLabel,
    QHBoxLayout,
    QMessageBox,
)
import sqlite3


class PlannerDialog(QDialog):
    def __init__(self, date_str, parent=None):
        super().__init__(parent)
        self.date_str = date_str
        self.setWindowTitle(f"Планирование питания на {date_str}")
        self.setGeometry(300, 300, 350, 200)

        main_layout = QVBoxLayout(self)

        main_layout.addWidget(
            QLabel(f"Выберите рецепт для планирования на {date_str}:")
        )

        self.recipe_combo = QComboBox()
        self.meal_type_combo = QComboBox()
        self.meal_type_combo.addItems(["Завтрак", "Обед", "Ужин"])

        layout_top = QHBoxLayout()
        layout_top.addWidget(self.recipe_combo)
        layout_top.addWidget(self.meal_type_combo)
        main_layout.addLayout(layout_top)

        self.save_btn = QPushButton("Сохранить план")
        self.save_btn.clicked.connect(self.save_plan)
        main_layout.addWidget(self.save_btn)

        self.load_recipes()

    def load_recipes(self):
        try:
            conn = sqlite3.connect("recipe_book.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM Recipes")
            recipes = cursor.fetchall()
            conn.close()

            for recipe_id, name in recipes:
                self.recipe_combo.addItem(name, recipe_id)

            if not recipes:
                QMessageBox.warning(
                    self, "Предупреждение", "Сначала добавьте рецепты в библиотеку"
                )
                self.save_btn.setEnabled(False)

        except sqlite3.Error as e:
            QMessageBox.critical(
                self, "Ошибка БД", f"Не удалось загрузить рецепты: {e}"
            )

    def save_plan(self):
        recipe_id = self.recipe_combo.currentData()
        meal_type = self.meal_type_combo.currentText()

        if not recipe_id:
            QMessageBox.warning(self, "Ошибка", "Не выбран рецепт")
            return

        try:
            conn = sqlite3.connect("recipe_book.db")
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM Meal_Plan WHERE date = ? AND meal_type = ?",
                (self.date_str, meal_type),
            )

            cursor.execute(
                "INSERT INTO Meal_Plan (date, recipe_id, meal_type) VALUES (?, ?, ?)",
                (self.date_str, recipe_id, meal_type),
            )
            conn.commit()
            conn.close()
            QMessageBox.information(
                self, "Успех", f"План '{meal_type}' на {self.date_str} сохранен"
            )
            self.accept()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось сохранить план: {e}")
