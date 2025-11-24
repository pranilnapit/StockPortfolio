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
def portfolio():
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
    rows = Stock.get_all_stocks()
    return render_template('stocks.html', rows=rows)

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