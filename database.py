import sqlite3


def init_db():
    try:
        conn = sqlite3.connect('recipe_book.db')
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            instructions TEXT NOT NULL,
            image_path TEXT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Recipe_Ingredients (
            recipe_id INTEGER NOT NULL,
            ingredient_id INTEGER NOT NULL,
            quantity TEXT,
            PRIMARY KEY (recipe_id, ingredient_id),
            FOREIGN KEY (recipe_id) REFERENCES Recipes (id) ON DELETE CASCADE,
            FOREIGN KEY (ingredient_id) REFERENCES Ingredients (id) ON DELETE CASCADE
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Meal_Plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            recipe_id INTEGER NOT NULL,
            meal_type TEXT,
            FOREIGN KEY (recipe_id) REFERENCES Recipes (id)
        )
        ''')

        conn.commit()
    except sqlite3.Error as e:
        # mb print e
        pass
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    init_db()