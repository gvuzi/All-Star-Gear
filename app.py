from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secretkey'


def init_db():
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL           
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized and users table created.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(f"Received registration data: Email = {email}, Password = {password}")

        conn = sqlite3.connect('data/AllStarDatabase.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO users (email,password) VALUES (?,?)               
            ''', (email, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "ERROR: Email already registered with AllStars account"
        finally:
            conn.close()

        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email =request.form.get('email')
        password= request.form.get('password')
        conn = sqlite3.connect('data/AllStarDatabase.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM users WHERE email = ? AND password = ?
        ''', (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id']= user[0]
            return redirect(url_for('index'))
        else:
            return "Invalid email for password", 401
    return render_template('login.html')


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM items
        WHERE name LIKE ? OR category LIKE ?
    ''' , ('%' + query + '%', '%' + query + '%'))
    items = cursor.fetchall()
    conn.close()
    return render_template('search_results.html', items=items)

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = cursor.fetchone()
    conn.close()
    if item:
        return render_template('item_detail.html', item=item)
    else:
        return "Item not found", 404


@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    cursor.execute('SELECT items FROM carts WHERE user_id = ?', (user_id))
    cart = cursor.fetchdone()

    if cart:
        items = cart[0].splite(',')
        if str(item_id) not in items:
            items.append(str(item_id))
        items_str = ','.join(items)
        cursor.execute('UPDATE carts SET items = ? WHERE user_id = ?',(items_str,user_id))
    else:
        cursor.execute('INSERT INTO carts (user_id,items) VALUES (?,?)',(user_id, str(item_id)))

    conn.commit()
    conn.close()
    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id= session['user_id']

    cart_items = []
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    cursor.execute('SELECT items FROM carts WHERE id = ?', (user_id,))
    cart = cursor.fetchone()
    items=[]

    if cart:
        item_ids = cart[0].split(',')
        for item_id in item_ids:
            cursor.execute('SELECT * FROM items WHERE id = ?',(item_id,))
            item= cursor.fetchone()
            if item:
                cart_items.append(item)
    conn.close()
    return render_template('cart.html', cart_items=cart_items)

if __name__=='__main__':
    init_db()
    app.run(debug=True, port=5500)
