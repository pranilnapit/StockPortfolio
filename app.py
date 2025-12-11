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

@app.route('/')
def home():
    if "user_id" in session:
        return render_template('dashboard.html')
    
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
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM investments where user_id = %s", (session['user_id'],))
    investments = cursor.fetchall()
    
    total_value = 0 
    total_cost = 0
    
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
        
    return render_template('dashboard.html', investments=updated_investments, total_value=round(total_value,2), total_cost=round(total_cost,2), profit_loss=round(profit_loss,2))


@app.route('/add_investment', methods=['GET', 'POST'])
def add_investment():
    if "user_id" not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        symbol = request.form['symbol'].upper()
        category = request.form['category']
        quantity = int(request.form['quantity'])
        buy_price = float(request.form['buy_price'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO investments (user_id, symbol, category, quantity, buy_price)
            VALUES (%s, %s, %s, %s, %s)
        """
        data = (session['user_id'], symbol, category, quantity, buy_price)
        cursor.execute(insert_query, data)
        conn.commit()
        conn.close()
        
        return redirect(url_for('dashboard'))
    return render_template('add_investment.html')

@app.route('/delete/<int:id>')
def delete_investment(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    delete_query = "DELETE FROM investments WHERE id = %s AND user_id = %s"
    cursor.execute(delete_query, (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_investment(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        quantity = float(request.form['quantity'])
        buy_price = float(request.form['buy_price'])
        
        update_query = """UPDATE investments SET quantity = %s, buy_price = %s
                          WHERE id = %s AND user_id = %s"""
        cursor.execute(update_query, (quantity, buy_price, id, session['user_id']))
        conn.commit()
        
        conn.close()
        return redirect(url_for('dashboard'))
    
    query = "SELECT * FROM investments WHERE id = %s AND user_id = %s"
    cursor.execute(query, (id, session['user_id']))
    investment = cursor.fetchone()
    
    return render_template('edit_investment.html', investment=investment)

if __name__ == '__main__':
    app.run(debug=True)