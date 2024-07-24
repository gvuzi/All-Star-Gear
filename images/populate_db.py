
import sqlite3

#Initializes database with hardcoded items
def populate_items():
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    items = [                                                   
        ('Tennis Racket', 'Tennis racket with extra light frame and stable sring pattern for maximum control', 99.99, 'Tennis','images/tennisracket.jpg'),
        ('Hockey Skates', "Thermoformable skates, made for enhanced comfort and fit", 139.99, 'Hockey','images/hockeyskates.jpg'),
        ('Punching Bag', 'Made with maximum impact absorption foam and fiber-sand for intense striking', 249.99, 'Boxing', 'images/punchingbag.jpg'),
        ('Basketball', 'High endurance basketball', 29.99, 'Basketball','images/basketball.png'),
        ('Boxing Gloves', 'Made for comfort boxing gloves', 39.99,'Boxing','images/boxinggloves.jpg'),
        ('Golf Club', 'Designed for maximum inertia and exceptional distance', 129.99, 'Golf', 'images/golfclub.jpg'),
        ('Football', 'Leather football made with modernized design for maximum control, grip and performance', 79.99, 'Football', 'images/football.jpg'),
        ('Golf Ball', 'Ideal for perfect aerodynamics and smooth feel', 9.99, 'Golf', 'images/golfball.jpg'),
        ('Volleyball', 'Lightweight volleyball made extra strong adhesive for an extended lifespan', 29.99,'Volleyball','images/Volleyball.jpg'),
        ('Soccer Ball', 'Durable soccer ball made with modern stitch pattern for increased distance and control', 19.99, 'Soccer','images/soccerball.jpg'),
        ('Leather Speed Bag', 'Rare imported leath for extended durability and smooth return', 49.99, 'Boxing', 'images/speedpunchingbag.jpg'),
        ('Tennis Ball', 'Single tennis ball, woven with natural rubber for increased durability', 8.99, 'Tennis', 'images/tennisball.jpg')
    ]
    #Adds all created items into database
    cursor.executemany(''' INSERT INTO items (name, description, price, category, image) VALUES (?, ?, ?, ?, ?)''', items)
    conn.commit()
    conn.close()

#Populates database if this script if ran directly
if __name__ == '__main__':
    populate_items()