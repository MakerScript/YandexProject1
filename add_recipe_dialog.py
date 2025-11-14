from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QFileDialog,
    QHBoxLayout,
)
import sqlite3


class AddRecipeDialog(QDialog):
    def __init__(self, parent=None, recipe_data=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить/Редактировать рецепт")
        self.recipe_id = recipe_data[0] if recipe_data else None

        main_layout = QVBoxLayout(self)

        self.name_input = QLineEdit(recipe_data[1] if recipe_data else "")
        self.instructions_input = QTextEdit(recipe_data[2] if recipe_data else "")
        self.image_path = recipe_data[3] if recipe_data and len(recipe_data) > 3 else ""

        main_layout.addWidget(QLabel("Название рецепта:"))
        main_layout.addWidget(self.name_input)

        main_layout.addWidget(QLabel("Инструкции:"))
        main_layout.addWidget(self.instructions_input)

        img_layout = QHBoxLayout()
        self.img_label = QLabel(
            self.image_path if self.image_path else "Изображение не выбрано"
        )
        self.img_btn = QPushButton("Выбрать фото")
        self.img_btn.clicked.connect(self.select_image)
        img_layout.addWidget(self.img_label)
        img_layout.addWidget(self.img_btn)
        main_layout.addLayout(img_layout)

        main_layout.addWidget(QLabel("Ингредиенты (через запятую):"))
        self.ingredients_input = QLineEdit()
        main_layout.addWidget(self.ingredients_input)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.accept)
        main_layout.addWidget(self.save_button)

        if self.recipe_id:
            self.load_ingredients()

    def select_image(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Выбрать изображение", "", "Images (*.png *.jpg *.jpeg)"
        )
        if fname:
            self.image_path = fname
            self.img_label.setText(fname)

    def load_ingredients(self):
        try:
            conn = sqlite3.connect("recipe_book.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT T2.name FROM Recipe_Ingredients T1 
                JOIN Ingredients T2 ON T1.ingredient_id = T2.id 
                WHERE T1.recipe_id = ?
            """,
                (self.recipe_id,),
            )

            ingredients = [row[0] for row in cursor.fetchall()]
            self.ingredients_input.setText(", ".join(ingredients))
            conn.close()
        except sqlite3.Error:
            pass

    def get_data(self):
        return (
            self.name_input.text(),
            self.instructions_input.toPlainText(),
            self.image_path,
            self.ingredients_input.text(),
        )
