import sqlite3

def add_availability_column():
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE items ADD COLUMN availability TEXT DEFAULT "In Stock"')
        conn.commit()
        print("Column added successfully.")
    except sqlite3.OperationalError as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_availability_column()
