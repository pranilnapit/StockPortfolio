from flask import Flask, render_template, request, redirect, session, url_for, flash
import pymysql
import yfinance as yf
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configurations
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='123456789',
        database='stockportfolio',
        cursorclass=pymysql.cursors.DictCursor # To return results as dictionaries
    )
    
class Stock:
    def __init__(self, stockName, buyDate, quantity, buyPrice):
        self.stockName = stockName
        self.buyDate = buyDate
        self.quantity = quantity
        self.buyPrice = buyPrice
        
    @classmethod
    def get_all_stocks(cls):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM portfolio")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    
    def new_entry(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO portfolio 
            (stockName, buyDate, quantity, buyPrice)
            VALUES (%s, %s, %s, %s)
        """
        
        data = (self.stockName, self.buyDate, self.quantity, self.buyPrice)
        cursor.execute(insert_query, data)
        conn.commit()
        cursor.close()
        conn.close()
    
# Function to get today's stock price
# def get_price_today(ticker):
#     stock = yf.Ticker(ticker)
#     todays_data = stock.history(period='1d')
#     if not todays_data.empty:
#         return todays_data['Close'].iloc[0]
#     return None


@app.route('/')
def home():
# First version
# ------------------------------------------------------
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     cursor.execute("SELECT * FROM portfolio")
#     rows = cursor.fetchall()
    
#     for row in rows:
#         try:
#             row['current_price'] = get_price_today(row['stockName'])
#             row['total_cost'] = float(row['current_price']) * int(row['quantity'])
#             row['total_value'] = float(row['buyPrice']) * int(row['quantity'])
#             row['profit_loss'] = row['total_cost'] - row['total_value']
#         except Exception as e:
#             row['current_price'] = None
#             row['total_cost'] = None
#             row['total_value'] = None
#             row['profit_loss'] = None
        
#     conn.close()
#     return render_template('portfolio.html', stocks=rows)
# ------------------------------------------------------
# Second version
# ------------------------------------------------------
    # conn = get_db_connection()
    # cursor = conn.cursor() # Create a cursor object
    
    # cursor.execute("Select * from portfolio") # Execute a query
    # rows = cursor.fetchall() # Fetch all results
    
    # cursor.close()
    # conn.close()
    
# ------------------------------------------------------
# Using the class method to get all stocks

    if "user_id" in session:
        rows = Stock.get_all_stocks()
        return render_template('stocks.html', rows=rows)
    
    return redirect(url_for('login'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(insert_query, (username, password))
        conn.commit()
        
        flash('Registration successful! Please log in.', 'success')
        
        return redirect(url_for('login'))
        
    return render_template('register.html')
        
        
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    rows = Stock.get_all_stocks()
    conn = get_db_connection()
    
    investments = conn.execute("SELECT * FROM investments where user_id = %s", (session['user_id'],)).fetchall()
    
    total_value, total_cost = 0
    
    updated_investments = []
    for inv in investments:
        try:
            #fetching live price using yfinance
            ticker = yf.Ticker(inv["symbol"])
            live_price = ticker.history(period='1d')['Close'].iloc[-1]
        except Exception:
            live_price = 0 # Default to 0 if fetching fails
            
        current_value = live_price * inv["quantity"]
        cost = inv["quantity"] * inv["buy_price"]
        
        total_value += current_value
        total_cost += cost
        
        updated_investments.append({
            "id": inv["id"],
            "symbol": inv["symbol"],
            "category": inv["category"],
            "quantity": inv["quantity"],
            "buy_price": inv["buy_price"],
            "current_price": round(live_price, 2),
            "value": round(current_value, 2),
            "profit_loss": round(current_value - cost, 2)
        })
        
    profit_loss = total_value - total_cost
        
    return render_template('dashboard.html', rows=rows, investments=updated_investments, total_value=round(total_value,2), total_cost=round(total_cost,2), profit_loss=round(profit_loss,2))


@app.route('/add', methods=['GET', 'POST'])
def add_stock():
    
    # First version
    # ------------------------------------------------------
    # if request.method == 'POST':
    #     stockName = request.form['stockName'].upper()
    #     buyDate = request.form['buyDate']
    #     quantity = int(request.form['quantity'])
    #     buyPrice = request.form['buyPrice']
        
    #     conn = get_db_connection()
    #     cursor = conn.cursor()
        
    #     query = """
    #         INSERT INTO portfolio (stockName, buyDate, quantity, buyPrice)
    #         VALUES (%s, %s, %s, %s)
    #     """
    #     data = (stockName, buyDate, quantity, buyPrice)
    #     cursor.execute(query, data)
    #     conn.commit()
    #     conn.close()
    
    # Second version
    if request.method == 'POST':
        print("POST received")
        data = Stock(
            stockName = request.form['stockName'].upper(),
            buyDate = request.form['buyDate'],
            quantity = int(request.form['quantity']),
            buyPrice = request.form['buyPrice']
        )
        data.new_entry()
        
        return redirect('/')
    return render_template('add.html')

@app.route('/delete', methods = ['POST'])
def delete_stock():
    id = request.form['id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        delete_query = "DELETE FROM portfolio WHERE id = %s"
        cursor.execute(delete_query, (id,))
        conn.commit()
        conn.close()
    return redirect('/')

@app.route('/edit', methods=['Get', 'POST'])
def edit_stock():
    if request.method == 'GET':
        stock_id = request.args.get('id')
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM portfolio WHERE id = %s", (stock_id,))
        stock = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return render_template('edit.html', stock=stock)
    
    if request.method == 'POST':
        stock_id = request.form.get('id')  
    
        stockName = request.form['stockName'].upper()
        buyDate = request.form['buyDate']
        quantity = int(request.form['quantity'])
        buyPrice = request.form['buyPrice']

        conn = get_db_connection()
        cursor = conn.cursor()

        update_query = """
            UPDATE portfolio
            SET stockName = %s, buyDate = %s, quantity = %s, buyPrice = %s
            WHERE id = %s
        """
        data = (stockName, buyDate, quantity, buyPrice, stock_id)
        cursor.execute(update_query, data)
        conn.commit()
        conn.close()

        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)