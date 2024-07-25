from flask import Flask, url_for, redirect, render_template, session, request, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'secretkey'

# Initialize database
def init_db():
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    cursor.execute(''' CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL )''')
    cursor.execute(''' CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, price REAL, category TEXT, image TEXT)''')
    cursor.execute(''' CREATE TABLE IF NOT EXISTS carts (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, item_id INTEGER, amount INTEGER)''')
    conn.commit()
    conn.close()

# Routes and logic
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_started', methods=['GET'])
def get_started():
    if 'user_id' in session:
        return redirect(url_for('store'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('edit_profile'))
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        cursor.execute(''' INSERT INTO users (email, password) VALUES (:email, :password)''', {'email': email, 'password': password})
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/store')
def store():
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    cursor.execute(''' SELECT * FROM items ''')
    allItems = cursor.fetchall()
    conn.close()
    return render_template('store.html', items=allItems)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('edit_profile'))
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        cursor.execute('''SELECT id FROM users WHERE email = :email AND password = :password ''', {'email': email, 'password': password})
        userFound = cursor.fetchone()
        conn.close()
        if userFound:
            session['user_id'] = userFound[0]
            return redirect(url_for('index'))
        else:
            return "Email or password is incorrect"
    return render_template('login.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session['user_id']
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        cursor.execute('''UPDATE users SET email = :email, password = :password WHERE id = :user_id''', {'email': email, 'password': password, 'user_id': user_id})
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    cursor.execute('''SELECT email, password FROM users WHERE id = :user_id''', {'user_id': user_id})
    user_data = cursor.fetchone()
    email, password = user_data
    conn.close()
    return render_template('edit_profile.html', email=email, password=password)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

# Updated search route with sorting functionality
@app.route('/search', methods=['GET'])
def search():
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    userQuery = request.args.get('query', '')
    sort_by = request.args.get('sort_by', 'relevance')

    # Base query
    query = "SELECT * FROM items WHERE name LIKE ? OR category LIKE ?"
    params = ('%' + userQuery + '%', '%' + userQuery + '%')

    # Modify query based on sorting
    if sort_by == 'price_asc':
        query += " ORDER BY price ASC"
    elif sort_by == 'price_desc':
        query += " ORDER BY price DESC"
    elif sort_by == 'availability':
        query += " ORDER BY availability DESC"  # Assuming you have an 'availability' column

    cursor.execute(query, params)
    matchingItems = cursor.fetchall()
    conn.close()
    return render_template('search_results.html', items=matchingItems)

@app.route('/item/<item_id>')
def item_detail(item_id):
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM items WHERE id = :item_id', {'item_id': item_id})
    clickedItem = cursor.fetchone()
    conn.close()
    if clickedItem:
        return render_template('item_detail.html', item=clickedItem)

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    if 'user_id' not in session:
        return redirect(url_for('login'))
    currUser = session['user_id']
    cursor.execute('SELECT amount FROM carts WHERE user_id = :currUser AND item_id = :item', {'currUser': currUser, 'item': item_id})
    cart = cursor.fetchone()
    if cart:
        quantity = cart[0] + 1
        cursor.execute('UPDATE carts SET amount = :quantity WHERE user_id = :currUser AND item_id = :item_id', {'quantity': quantity, 'currUser': currUser, 'item_id': item_id})
    else:
        cursor.execute('INSERT INTO carts (user_id, item_id, amount) VALUES (?, ?, ?)', (currUser, item_id, 1))
    conn.commit()
    conn.close()
    return redirect(url_for('item_detail', item_id=item_id))

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    currUser = session['user_id']
    if request.method == 'POST':
        # Update item quantities
        quantities = request.form.getlist('quantity')
        item_ids = request.form.getlist('item_id')
        for item_id, quantity in zip(item_ids, quantities):
            cursor.execute('UPDATE carts SET amount = ? WHERE user_id = ? AND item_id = ?', (quantity, currUser, item_id))
        conn.commit()

    cursor.execute('''
        SELECT items.id, items.name, items.description, items.price, items.category, items.image, carts.amount 
        FROM carts
        JOIN items ON carts.item_id = items.id 
        WHERE carts.user_id = :currUser 
    ''', {'currUser': currUser})
    fullCart = cursor.fetchall()

    # Calculate subtotal and taxes
    subtotal = sum(item[3] * item[6] for item in fullCart)
    tax_rate = 0.0825
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax, 2)

    discount = 0
    discount_code = request.form.get('discount_code')
    if discount_code == 'SAVE10':
        discount = round(total * 0.10, 2)
    elif discount_code == 'SAVE20':
        discount = round(total * 0.20, 2)
    total = round(total - discount, 2)

    conn.close()
    return render_template('cart.html', cart_items=fullCart, subtotal=subtotal, tax=tax, total=total, discount=discount)

@app.route('/remove_item/<int:item_id>', methods=['POST'])
def remove_item(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    currUser = session['user_id']
    cursor.execute('DELETE FROM carts WHERE user_id = ? AND item_id = ?', (currUser, item_id))
    conn.commit()
    conn.close()
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Process checkout (collect user details, process payment, etc.)
    flash('Order placed successfully!', 'success')
    return redirect(url_for('cart'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5500)
