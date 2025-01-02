from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('inventory.db')  # Connects to or creates the database file
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_name TEXT NOT NULL,
            player TEXT,
            year INTEGER,
            condition TEXT,
            quantity INTEGER DEFAULT 1,
            purchase_price REAL,
            purchase_date TEXT,
            set_name TEXT,
            card_number TEXT,
            grading TEXT,
            sale_price REAL,
            sale_date TEXT,
            vendor_or_buyer TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Fetch summary data
    cursor.execute('SELECT COUNT(*) FROM inventory')
    total_cards = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(purchase_price * quantity) FROM inventory')
    total_value = cursor.fetchone()[0] or 0  # Default to 0 if no data

    cursor.execute('SELECT SUM(sale_price * quantity) FROM inventory')
    total_sales = cursor.fetchone()[0] or 0

    conn.close()

    return render_template('home.html', total_cards=total_cards, total_value=total_value, total_sales=total_sales)



@app.route('/add', methods=['GET', 'POST'])
def add_card():
    if request.method == 'POST':
        # Get data from the form
        card_name = request.form['card_name']
        player = request.form['player']
        year = request.form['year']
        condition = request.form['condition']
        quantity = request.form['quantity']
        purchase_price = request.form['purchase_price']
        purchase_date = request.form['purchase_date']
        set_name = request.form['set_name']
        card_number = request.form['card_number']
        grading = request.form['grading']
        sale_price = request.form['sale_price']
        sale_date = request.form['sale_date']
        vendor_or_buyer = request.form['vendor_or_buyer']

        # Insert into the database
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inventory (card_name, player, year, condition, quantity, purchase_price, purchase_date,
                                   set_name, card_number, grading, sale_price, sale_date, vendor_or_buyer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (card_name, player, year, condition, quantity, purchase_price, purchase_date, set_name,
              card_number, grading, sale_price, sale_date, vendor_or_buyer))
        conn.commit()
        conn.close()

        # Redirect to the homepage
        return redirect(url_for('home'))
    return render_template('add_card.html')


@app.route('/view', methods=['GET', 'POST'])
def view_inventory():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Base SQL query
    query = "SELECT * FROM inventory"
    filters = []
    conditions = []

    # Handle search and filters
    if request.method == 'POST':
        search = request.form.get('search', '').strip()
        player_filter = request.form.get('player', '').strip()
        year_filter = request.form.get('year', '').strip()

        if search:
            conditions.append("(card_name LIKE ? OR player LIKE ?)")
            filters.extend([f"%{search}%", f"%{search}%"])
        if player_filter:
            conditions.append("player = ?")
            filters.append(player_filter)
        if year_filter:
            conditions.append("year = ?")
            filters.append(year_filter)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, filters)
    rows = cursor.fetchall()
    conn.close()
 # Pass a flag to indicate if no results are found
    no_results = len(rows) == 0
    return render_template('view_inventory.html', rows=rows, no_results=no_results)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_card(id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        # Get updated data from the form
        card_name = request.form['card_name']
        player = request.form['player']
        year = request.form['year']
        condition = request.form['condition']
        quantity = request.form['quantity']
        purchase_price = request.form['purchase_price']
        purchase_date = request.form['purchase_date']
        set_name = request.form['set_name']
        card_number = request.form['card_number']
        grading = request.form['grading']
        sale_price = request.form['sale_price']
        sale_date = request.form['sale_date']
        vendor_or_buyer = request.form['vendor_or_buyer']

        # Update the record
        cursor.execute('''
            UPDATE inventory
            SET card_name = ?, player = ?, year = ?, condition = ?, quantity = ?,
                purchase_price = ?, purchase_date = ?, set_name = ?, card_number = ?,
                grading = ?, sale_price = ?, sale_date = ?, vendor_or_buyer = ?
            WHERE id = ?
        ''', (card_name, player, year, condition, quantity, purchase_price, purchase_date,
              set_name, card_number, grading, sale_price, sale_date, vendor_or_buyer, id))
        conn.commit()
        conn.close()
        return redirect('/view')

    # Fetch the current data
    cursor.execute('SELECT * FROM inventory WHERE id = ?', (id,))
    card = cursor.fetchone()
    conn.close()
    return render_template('edit_card.html', card=card)

@app.route('/delete/<int:id>', methods=['GET'])
def delete_card(id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM inventory WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash("Card deleted successfully!")
    return redirect('/view')



if __name__ == '__main__':
    app.run(debug=True)