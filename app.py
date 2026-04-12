from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector, dbfunc, sys
from mysql.connector import errorcode
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key in production
# use python -c 'import secrets; print(secrets.token_hex(32))' to generate for production

@app.route('/')
@app.route('/index')
def index():
    conn = dbfunc.getConnection()
    if not conn.is_connected():
        print('MySQL Connection Error')
        return "DB Connection Error. Check console for more details.", 500
    
    dbcursor = conn.cursor(dictionary=True) # Creates cursor object to run queries and execute statements
  
    # Select locations for dropdown
    dbcursor.execute('SELECT DISTINCT Location FROM venues WHERE Location IS NOT NULL ORDER BY Location ASC')
    locations = [row['Location'] for row in dbcursor.fetchall()]

    # Select categories for dropdown
    dbcursor.execute('SELECT DISTINCT Category_name FROM categories WHERE Category_name IS NOT NULL ORDER BY Category_name ASC')
    categories = [row['Category_name'] for row in dbcursor.fetchall()]

    # Select venues types for dropdown
    dbcursor.execute('SELECT DISTINCT Type FROM venues WHERE Type IS NOT NULL ORDER BY Type ASC')
    venue_types = [row['Type'] for row in dbcursor.fetchall()]

    # Select venue name, description, image for venue carousel
    dbcursor.execute('SELECT Name, Description, Image_URL FROM venues WHERE Name IS NOT NULL AND Description IS NOT NULL AND Image_URL IS NOT NULL')
    venue_carousel = dbcursor.fetchall()

    dbcursor.close()
    conn.close()

    return render_template('index.html', locations=locations, categories=categories, venue_types=venue_types, venue_carousel=venue_carousel)

@app.route('/events')
def events():
    conn = dbfunc.getConnection()
    if not conn.is_connected():
        print('MySQL Connection Error')
        return "DB Connection Error. Check console for more details.", 500
    
    dbcursor = conn.cursor(dictionary=True) 

    # fetch all events from database
    dbcursor.execute('SELECT * FROM Event_Cards ORDER BY date ASC')
    fetched_events = dbcursor.fetchall()
    print(fetched_events) # Debugging log to verify data is fetched correctly
    for ev in fetched_events:
        ev['date'] = str(ev['date']) if ev['date'] else "" # Convert date to string for JSON serialization, handle NULL dates
        ev['end_date'] = str(ev['end_date']) if ev['end_date'] else "" # Convert end date to string for JSON serialization, handle NULL dates

    # fetch distinct venues and categories for dropdown filters dynamically from database
    dbcursor.execute('SELECT DISTINCT venue FROM Event_Cards WHERE venue IS NOT NULL ORDER BY venue ASC')
    venues = [row['venue'] for row in dbcursor.fetchall()]

    dbcursor.execute('SELECT DISTINCT category FROM Event_Cards WHERE category IS NOT NULL ORDER BY category ASC')
    categories = [row['category'] for row in dbcursor.fetchall()]

    dbcursor.close()
    conn.close()

    return render_template('events.html', events=fetched_events, venues=venues, categories=categories)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # if user is already logged in, send them to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    # if POST request, process signup form data
    if request.method == 'POST':
        username = request.form.get('username', '').strip()  
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()  
        email = request.form.get('email', '').strip()  
        password = request.form.get('password', '').strip()
        phone_number = request.form.get('phone_number', '').strip()

        avatar_url = request.form.get('avatar_url', '').strip()
        # assign default avatar if none provided
        if not avatar_url:
            avatar_url = url_for('static', filename='img/ProfilePic.png')

        confirm_password = request.form.get('confirm_password', '').strip()
        terms = request.form.get('terms')  # Will be 'on' if checked, None if not  

        # Backend validation
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('signup'))
        if not terms:
            flash('Please agree to the terms and conditions.', 'danger')
            return redirect(url_for('signup'))

        conn = dbfunc.getConnection()
        if not conn.is_connected():
            print('MySQL Connection Error')
            return "DB Connection Error. Check console for more details.", 500
        
        dbcursor = conn.cursor(dictionary=True)

        # Check if email or username already exists
        dbcursor.execute('SELECT * FROM Users WHERE Email = %s OR Username = %s', (email, username))
        if dbcursor.fetchone(): # if record exists
            flash('Email or username already exists. Please log in.', 'warning')
            dbcursor.close()
            conn.close()
            return redirect(url_for('signup'))

        # Hash the password before storing
        # generate_password_hash automatically salts password and encrypts using PBKDF2 algorithm
        hashed_password = generate_password_hash(password)

        # Insert new user into database
        try:
            query = 'INSERT INTO Users (Username, First_name, Last_name, Email, Password_hash, Phone_number, Avatar_URL, Terms_agreed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
            dbcursor.execute(query, (username, first_name, last_name, email, hashed_password, phone_number, avatar_url, terms))
            conn.commit()
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            print(f"Error inserting user: {err}")
            flash('An error occurred while creating your account. Please try again.', 'danger')
            return redirect(url_for('signup'))
        finally:
            dbcursor.close()
            conn.close()
    
    return render_template('sign-up.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        conn = dbfunc.getConnection()
        if not conn.is_connected():
            print('MySQL Connection Error')
            return "DB Connection Error. Check console for more details.", 500
        
        dbcursor = conn.cursor(dictionary=True)

        # Fetch user by email
        dbcursor.execute('SELECT * FROM Users WHERE Email = %s', (email,))
        user = dbcursor.fetchone()

        dbcursor.close()
        conn.close()

        # Check if user exists and hashed passord matches the typed password
        if user and check_password_hash(user['Password_hash'], password):
            # Log the user in by storing their info in session
            session['user_id'] = user['User_ID']
            session['username'] = user['Username']
            session['role'] = user['Role']

            flash(f'Welcome back, {user["First_name"] or user["Username"]}!', 'success')
            return redirect(url_for('index')) # change to dashboard later when implemented
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('login'))
        
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index')) # change to login page later when implemented




@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
        