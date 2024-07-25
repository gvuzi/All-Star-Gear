from flask import Flask
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('data/AllStarDatabase.db') #Connect to database
    cursor = conn.cursor()
    #Create users table where each entry has an id, an email and a password
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL )''')

    #Create users items table where each entry has an id, name, description, price, category and an image
    cursor.execute('''CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image TEXT NOT NULL )''')

    #Creates carts table where each entry has an id, user_id, item_id, amount, and foreign keys that ensure every 
    # user_id and item_id connect to an active user and item
    cursor.execute('''CREATE TABLE IF NOT EXISTS carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, item_id INTEGER NOT NULL, amount INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(item_id) REFERENCES items(id) ) ''')
    
    #Saves changes and close connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()