
import sqlite3

def populate_items():
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    items = [                                                   
        ('Tennis Racket', 'High-quality tennis racket', 99.99, 'Tennis','images/tennisracket.jpg'),
        ('Basketball', 'Official size basketball', 29.99, 'Basketball','images/basketball.png'),
        ('Soccer Ball', 'Durable soccer ball for practice', 19.99, 'Soccer','images/soccerball.jpg'),
        ('Tennis Ball', 'Single tennis ball, woven with natural rubber for increased durability', 8.99, 'Tennis', 'images/tennisball.jpg')
    ]
    cursor.executemany('''
        INSERT INTO items (name, description, price, category, image_url) VALUES (?, ?, ?, ?, ?)
    ''', items)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    populate_items()