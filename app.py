from flask import Flask, render_template, request, redirect
import pymysql
import yfinance as yf

app = Flask(__name__)

# Database configurations
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='123456789',
        database='stockportfolio',
        cursorclass=pymysql.cursors.DictCursor # To return results as dictionaries
    )
    
# Function to get today's stock price
def get_price_today(ticker):
    stock = yf.Ticker(ticker)
    todays_data = stock.history(period='1d')
    if not todays_data.empty:
        return todays_data['Close'].iloc[0]
    return None


@app.route('/')
def portfolio():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM portfolio")
    rows = cursor.fetchall()
    
    for row in rows:
        try:
            row['current_price'] = get_price_today(row['stockName'])
            row['total_cost'] = float(row['current_price']) * int(row['quantity'])
            row['total_value'] = float(row['buyPrice']) * int(row['quantity'])
            row['profit_loss'] = row['total_cost'] - row['total_value']
        except Exception as e:
            row['current_price'] = None
            row['total_cost'] = None
            row['total_value'] = None
            row['profit_loss'] = None
        
    conn.close()
    return render_template('portfolio.html', stocks=rows)

@app.route('/add', methods=['GET', 'POST'])
def add_stock():
    if request.method == 'POST':
        stockName = request.form['stockName'].upper()
        buyDate = request.form['buyDate']
        quantity = int(request.form['quantity'])
        buyPrice = request.form['buyPrice']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO portfolio (stockName, buyDate, quantity, buyPrice)
            VALUES (%s, %s, %s, %s)
        """
        data = (stockName, buyDate, quantity, buyPrice)
        cursor.execute(query, data)
        conn.commit()
        conn.close()
        
        return redirect('/')
    
    return render_template('add.html')


if __name__ == '__main__':
    app.run(debug=True)