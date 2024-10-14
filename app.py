from flask import Flask, render_template, request, redirect, flash, session, url_for, g
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import requests
from bs4 import BeautifulSoup
import smtplib
import os
from dotenv import load_dotenv  # Import the load_dotenv function
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.DEBUG)
# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)


app.config['SECRET_KEY'] = 'your_secret_key'

# A list to store added URLs
added_urls = []
# Access environment variables
my_email = os.getenv("my_email")
app_password = os.getenv("app_password")
def monitor_all_prices():
    print("Starting monitor_all_prices")
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        print(f"Processing user_id={user_id}")
        for product_name, url, threshold_price in get_user_urls(user_id):
            user_email = get_user_email(user_id)
            print(f"Calling monitor_price for user_email={user_email}, url={url}")
            monitor_price(product_name, url, threshold_price, user_email)
    print("Finished monitor_all_prices")



from flask import g

def get_all_user_ids():
    with app.app_context():
        if 'db' not in g:
            g.db = sqlite3.connect('users.db')
        cursor = g.db.cursor()
        cursor.execute('SELECT id FROM users')
        user_ids = [row[0] for row in cursor.fetchall()]
    return user_ids

@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        g.db.close()

def monitor_price(product_name, url, threshold_price, user_email):
    print(f"Processing {url} for {user_email}")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    accept_language = "en-US,en;q=0.9"
    response = requests.get(url, headers={'user-agent': user_agent, 'accept-language': accept_language})
    res = response.text
    soup = BeautifulSoup(res, "lxml")

    # Find the price element using a more robust selector
    price_element = soup.find("span", {"class": "a-offscreen"})

    if price_element:
        price = price_element.get_text()
        print(f"Raw price: {price}")

        # Extract the price without currency
        price_without_currency = price.split("$")[1] if "$" in price else None

        if price_without_currency is not None:
            price_as_float = float(price_without_currency)
            print(price_as_float)

            if price_as_float < threshold_price:
                with open("message.txt") as f:
                    contents = f.read()
                    contents = contents.replace("[name]", str(product_name))
                    contents = contents.replace("[price]", str(price_as_float))

                with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
                    connection.starttls()
                    connection.login(user=my_email, password=app_password)
                    connection.sendmail(from_addr=my_email, to_addrs=user_email, msg=f"Subject:Hello\n\n{contents}")
    else:
        print("Price element not found on the page.")


# Function to create the user table
def create_user_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,  -- Add this line
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def create_user_urls_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            url TEXT NOT NULL,
            threshold FLOAT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()


def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.check_password_hash(user[2], password):
        return user

    return None



def save_user_url(user_id, product_name, url, threshold):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_urls (user_id, product_name, url, threshold) VALUES (?, ?, ?, ?)',
                   (user_id, product_name, url, threshold))
    conn.commit()
    conn.close()


def get_user_email(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    user_email = cursor.fetchone()[0]
    conn.close()
    return user_email


def get_user_urls(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT product_name, url, threshold FROM user_urls WHERE user_id = ?', (user_id,))
    user_urls = cursor.fetchall()
    conn.close()
    return user_urls


def remove_url(user_id, url):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_urls WHERE user_id = ? AND url = ?', (user_id, url))
    conn.commit()
    conn.close()


@app.route('/remove_url', methods=['POST'])
def remove_url_route():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Get user's email
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    user_email = cursor.fetchone()[0]
    conn.close()

    # Handle remove URL request
    if request.method == 'POST':
        url_to_remove = request.form['url']
        remove_url(user_id, url_to_remove)
        flash(f'URL removed: {url_to_remove}', 'success')

    # Get user-specific URLs from the database
    user_urls = get_user_urls(user_id)

    return render_template('index.html', user_email=user_email, urls=user_urls)


@app.route('/')
def welcome():
    return render_template('welcome.html')


@app.route('/login', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = authenticate_user(username, password)

        if user:
            session['user_id'] = user[0]  # Store user ID in session
            flash('Login successful', 'success')
            return redirect(url_for('index'))  # Redirect to the dashboard

        flash('Invalid username or password', 'danger')

    return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Check if the username or email already exists
        cursor.execute('SELECT * FROM users WHERE username=? OR email=?', (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            flash('Username or email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        # If the username and email are unique, proceed with registration
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                       (username, email, hashed_password))
        conn.commit()
        conn.close()

        flash('Registration successful', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logout successful', 'success')
    return redirect(url_for('login'))


@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard', 'danger')
        return redirect(url_for('login'))

    global user_email
    user_id = session['user_id']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    user_email = cursor.fetchone()[0]  # Assuming email is the first column
    conn.close()

    # Sample form for entering URLs and thresholds
    if request.method == 'POST':
        url = request.form['url']
        threshold = float(request.form['threshold'])

        # Get product name using web scraping
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        accept_language = "en-US,en;q=0.9"
        response = requests.get(url, headers={'user-agent': user_agent, 'accept-language': accept_language})
        res = response.text
        soup = BeautifulSoup(res, "lxml")
        product_name = soup.find(id="productTitle").get_text().strip()

        # Save the URL to the database
        save_user_url(user_id, product_name, url, threshold)

        # Monitor the price
        monitor_price(product_name, url, threshold, user_email)

        flash(f'URL added: {url} (Threshold: {threshold})', 'success')

    # Fetch and display user-specific URLs
    user_urls = get_user_urls(user_id)

    return render_template('index.html', user_email=user_email, urls=user_urls)


if __name__ == '__main__':
    create_user_table()  # Create the user table
    create_user_urls_table()
    # Schedule the monitor_all_prices function to run every hour with user_email as a parameter
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=monitor_all_prices, trigger="interval", minutes=3)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    app.run(debug=True, use_reloader= False)