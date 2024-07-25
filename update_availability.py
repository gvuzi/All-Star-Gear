import sqlite3

def update_availability():
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()

    # Update the availability of three specific items to "Out of Stock"
    item_ids_to_update = [2, 4, 6]  # IDs of Hockey Skates, Basketball, and Golf Club
    for item_id in item_ids_to_update:
        cursor.execute('UPDATE items SET availability = "Out of Stock" WHERE id = ?', (item_id,))
    
    conn.commit()
    print("Availability updated successfully.")
    conn.close()

if __name__ == "__main__":
    update_availability()
