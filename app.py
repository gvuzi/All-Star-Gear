from flask import Flask,url_for, redirect, render_template,session, request, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'secretkey' #Session key needed for user sessions and user login

#Connect python file to database script, initialize sql cursor and create users table
def init_db():
    conn =sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    cursor.execute(''' CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL )''')
    conn.commit()
    conn.close()

#Creates route to the homepage 
@app.route('/')
def index():
    return render_template('index.html')

#Creates route/function for when user presses Get Started
@app.route('/get_started', methods=['GET'])
def get_started():
    if 'user_id' in session: #If the user is signed in redirect them to the store page showing all items 
        return redirect(url_for('store'))
    return redirect(url_for('login')) #Prompts user to login if not logged in

#Create route/function that accepts GET and POST requests when user presses registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session: #If the user is signed in redirect them to the edit profile page
        return redirect(url_for('edit_profile'))
    #Connects to the database and initliazes sql cursor for database manipulation
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    if request.method == 'POST': #If user submitted registration request
        email =request.form.get('email') #Get submitted email
        password= request.form.get('password') #Get submitted password
        #Insert user entered values into a new entry in users table
        cursor.execute(''' INSERT INTO users (email,password) VALUES (:email,:password)''', {'email': email, 'password': password})
        conn.commit() #Saves changes to database
        conn.close() #Close connection
        return redirect(url_for('login')) #Sends user to login route
    return render_template('register.html') #Sends user to register page

#Creates a route/function to fetch all items from the database and display them through 'store.html'
@app.route('/store')
def store():
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor=conn.cursor()
    cursor.execute(''' SELECT * FROM items ''')
    allItems = cursor.fetchall()
    conn.close()
    return render_template('store.html',items=allItems)

#Create route/function that accepts GET and POST requests when user attempts to login
@app.route('/login', methods=['GET','POST'])
def login():
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        email =request.form.get('email') #Gets user given email
        password= request.form.get('password') #Gets user given password
        #Attempts to select the user with the given information from the users table
        cursor.execute('''SELECT id FROM users WHERE email = :email AND password = :password ''', {'email':email,'password':password})
        userFound = cursor.fetchone()
        conn.close()
        if userFound:
            session['user_id']= userFound[0] #If user is found, assign sessions user id to id of user found in database
            return redirect(url_for('index'))
        else:
            return "Email or password is incorrect"
    return render_template('login.html')

#Creates route/function that accepts GET and POST requests when user presses login icon in header when already logged in
@app.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    user_id = session['user_id']
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        email = request.form.get('email') #Gets user edited email
        password = request.form.get('password') #Gets user edited password
        #Updates user information in the user table
        cursor.execute('''UPDATE users SET email = :email, password = :password WHERE id = :user_id''', {'email':email, 'password':password, 'user_id': user_id})
        conn.commit() #Saves changes to database
        conn.close() #Close connection
        return redirect(url_for('index'))

    #Fetch current user information from the users table
    cursor.execute('''SELECT email, password FROM users WHERE id = :user_id''', {'user_id':user_id})
    user_data = cursor.fetchone()
    email, password = user_data;
    conn.close()

    return render_template('edit_profile.html', email=email, password=password) #Loads edit profile page with user information

#Creates route/function for when user logouts
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None) #Removes user_id token from session 
    return redirect(url_for('index'))

#Create route/function for when user attempts to search
@app.route('/search', methods=['GET'])
def search():
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    userQuery = request.args.get('query', '') #Gets search made by user
    #Searches for items that have the query made by the user anywhere in the category or name sections
    cursor.execute('''SELECT * FROM items WHERE name LIKE ? OR category LIKE ?''',('%' + userQuery + '%', '%' + userQuery + '%'))
    matchingItems = cursor.fetchall() #Gets all matching items from database result
    conn.close()
    return render_template('search_results.html', items=matchingItems) #Shows search results page with matching items found

#Creates route/function for when a user clicks on an item and retrieves the item_id of the item
@app.route('/item/<item_id>')
def item_detail(item_id):
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM items WHERE id = :item_id', {'item_id':item_id,}) #Selects item passed in as paramater from database
    clickedItem = cursor.fetchone() #Retrieves clicked item from database
    conn.close()
    if clickedItem:
        return render_template('item_detail.html',item=clickedItem) #Prints out item if found

#Creates route/function for adding a passed in item to a users cart 
@app.route('/add_to_cart/<int:item_id>', methods=['POST']) 
def add_to_cart(item_id):
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    if 'user_id' not in session: #Checks if the user is signed in, if not redirects to login screen
        return redirect(url_for('login'))
    currUser = session['user_id'] #Gets the user id of the current session so the correct shopping cart is accessed
    cursor.execute('SELECT amount FROM carts WHERE user_id = :currUser AND item_id = :item', {'currUser':currUser, 'item':item_id})
    cart = cursor.fetchone()
    if cart:
        #If the item is already in the cart, add another
        quantity =cart[0]+1
        #Updates the number of the item found in the cart in the database
        cursor.execute('UPDATE carts SET amount = :quantity WHERE user_id = :currUser AND item_id = :item_id', {'quantity':quantity, 'currUser':currUser,'item_id':item_id})
    else:
        #If the item is not already in the cart, add it
        cursor.execute('INSERT INTO carts (user_id, item_id, amount) VALUES (?, ?, ?)', (currUser,item_id, 1))
    conn.commit()
    conn.close()
    return redirect(url_for('item_detail',item_id=item_id))

#Creates route/function for user to view their carts content
@app.route('/cart')
def cart():
    if 'user_id' not in session: #If the user is not signed in redirect them to the login page
        return redirect(url_for('login'))
    conn = sqlite3.connect('data/AllStarDatabase.db')
    cursor = conn.cursor()
    currUser= session['user_id']
    #Retrieve all items and item information found in the current users cart
    cursor.execute('''
        SELECT items.id, items.name, items.description, items.price, items.category, items.image FROM carts
        JOIN items ON carts.item_id = items.id WHERE carts.user_id = :currUser ''', {'currUser':currUser,})
    fullCart = cursor.fetchall() #Gets all of the values returned from database
    conn.close()
    return render_template('cart.html', cart_items=fullCart)


#Initializes the database and runs Flask
if __name__=='__main__':
    init_db()
    app.run(debug=True, port=5500)
