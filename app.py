from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import mysql.connector, dbfunc, sys
from mysql.connector import errorcode
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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

        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        # Backend validation
        if password != confirm_password:
            if is_ajax:
                return jsonify({'success': False, 'message': 'Passwords do not match. Please try again.'})
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('signup'))
        if not terms:
            if is_ajax:
                return jsonify({'success': False, 'message': 'Please agree to the terms and conditions.'})
            flash('Please agree to the terms and conditions.', 'danger')
            return redirect(url_for('signup'))

        conn = dbfunc.getConnection()
        if not conn.is_connected():
            print('MySQL Connection Error')
            if is_ajax:
                return jsonify({'success': False, 'message': 'Database Connection Error.'})
            return "DB Connection Error. Check console for more details.", 500
        
        dbcursor = conn.cursor(dictionary=True)

        # Check if email or username already exists
        dbcursor.execute('SELECT * FROM Users WHERE Email = %s OR Username = %s', (email, username))
        if dbcursor.fetchone(): # if record exists
            dbcursor.close()
            conn.close()
            if is_ajax:
                return jsonify({'success': False, 'message': 'Email or username already exists. Please log in.'})
            flash('Email or username already exists. Please log in.', 'warning')
            return redirect(url_for('signup'))

        # Hash the password before storing
        # generate_password_hash automatically salts password and encrypts using PBKDF2 algorithm
        hashed_password = generate_password_hash(password)

        # Insert new user into database
        try:
            query = 'INSERT INTO Users (Username, First_name, Last_name, Email, Password_hash, Phone_number, Avatar_URL, Terms_agreed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
            dbcursor.execute(query, (username, first_name, last_name, email, hashed_password, phone_number, avatar_url, 1))
            conn.commit()
            if is_ajax:
                return jsonify({'success': True, 'message': 'Account created successfully! You can now log in.', 'redirect': url_for('login')})
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            print(f"Error inserting user: {err}")
            if is_ajax:
                return jsonify({'success': False, 'message': 'An error occurred while creating your account. Please try again.'})
            flash('An error occurred while creating your account. Please try again.', 'danger')
            return redirect(url_for('signup'))
        finally:
            dbcursor.close()
            conn.close()
    
    return render_template('sign-up.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index')) # change to dashboard later when implemented
    
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

        # Check if request is AJAX (for use in AJAx login without page reload)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        # Check if user exists and hashed passord matches the typed password
        if user and check_password_hash(user['Password_hash'], password):
            # Log the user in by storing their info in session
            session['user_id'] = user['User_ID']
            session['username'] = user['Username']
            session['role'] = user['Role']

            if is_ajax:
                return jsonify({'success': True, 'message': 'Login successful', 'redirect': url_for('index')}) # data.success hold result, data.message holds message in AJAX response
            
            # Fallback for non-AJAX login
            flash('Login successful! Welcome back, {}.'.format(user['First_name']), 'success')
            return redirect(url_for('index')) # change to dashboard later when implemented
        else:
            if is_ajax:
                return jsonify({'success': False, 'message': 'Invalid email or password.'})

            # Fallback for non-AJAX login
            flash('Invalid email or password. Please try again.', 'danger')
        
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index')) # change to login page later when implemented



@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    conn = dbfunc.getConnection()
    if not conn.is_connected():
        print('MySQL Connection Error')
        return "DB Connection Error. Check console for more details.", 500
    
    dbcursor = conn.cursor(dictionary=True)

    # Card 1: User Profile and Change info
    dbcursor.execute('SELECT Username, First_name, Last_name, Email, Phone_number, Join_date, Avatar_URL FROM Users WHERE User_ID = %s', (user_id,))
    user_profile = dbcursor.fetchone() # only one user should return

    # Format the date
    if user_profile and user_profile.get('Join_date'):
        user_profile['Join_date'] = user_profile['Join_date'].strftime('%B %Y') # Format date as Month Year
    else:
        user_profile['Join_date'] = "Recently Joined" # Fallback text if join date is missing

    
    # Card 2: Total Events Booked/Attended
    dbcursor.execute('SELECT COUNT(DISTINCT Event_ID) as Total_Booked FROM Bookings WHERE User_ID = %s', (user_id,))
    total_booked = dbcursor.fetchone()['Total_Booked'] # Just get total booked from returned dict



    # Card 3: Wallet Balance from VIEW
    dbcursor.execute('SELECT Balance FROM Wallet_Balance WHERE User_ID = %s', (user_id,))
    wallet_result = dbcursor.fetchone()
    # Check if row exists and 'Balance' is not empty
    if wallet_result and wallet_result['Balance'] is not None:
        wallet_balance = float(wallet_result['Balance'])
    else:
        wallet_balance = 0.00 # Default to 0.00


    # Card 4: Amount Spent in last 90 days (SUM(Negative Transactions)
    # Select the absoulte value of sum of transactions from transactions table of a certain user, where transaction_amount < 0 and transaction date >= now - 90 
    dbcursor.execute('''SELECT ABS(SUM(Amount)) AS Spent_90_Days
                     FROM Transactions
                     WHERE User_ID = %s
                     AND Amount < 0 AND Transaction_Date >= DATE_SUB(NOW(), INTERVAL 90 DAY)''', (user_id,))
    spent_result = dbcursor.fetchone()
    if spent_result and spent_result['Spent_90_Days'] is not None:
        spent_90_days = float(spent_result['Spent_90_Days'])
    else:
        spent_90_days = 0.00 # Default to 0.00


    # Card 5: 6-Month Spending Analysis
    six_mon_ago = datetime.now() - relativedelta(months=5)
    six_mon_ago = six_mon_ago.replace(day=1) # Set to first day of month to include full month in analysis
    six_mon_ago_str = six_mon_ago.strftime('%Y-%m-01') # Convert to string for SQL query

    dbcursor.execute('''SELECT DATE_FORMAT(Transaction_Date, '%Y-%m') AS Month, ABS(SUM(Amount)) AS Total_Spent
                     FROM Transactions
                     WHERE User_ID = %s
                     AND Amount < 0 AND Transaction_Date >= %s
                     GROUP BY Month
                     ORDER BY Month ASC''', (user_id, six_mon_ago_str,))
    
    spending_data = dbcursor.fetchall()

    # Formatting data for Chart.js
    chart_labels = []
    chart_values = []
    has_spending_activity = len(spending_data) > 0 # Check if there is any spending activity in the last 6 months

    if has_spending_activity:
        for row in spending_data:
            # Convert Year-Month formatted to Mon Year
            month_obj = datetime.strptime(row['Month'], '%Y-%m') # Parses datetime as a string
            chart_labels.append(month_obj.strftime('%b %Y')) # Format month as Mon Year for chart labels
            chart_values.append(float(row['Total_Spent'])) # Append total spent for each month to chart values



    # Card 6: Tickets Purchased (Using User_Ticket_Info VIEW)
    # This page will only show event.Title, tickets_purchased, total_price
    # Clicking on the card will redirect to separate tickets.html

    dbcursor.execute('''SELECT Title, Tickets_Purchased, Total_Price, Live_Status
                     FROM User_Ticket_Info
                     WHERE User_ID = %s
                     GROUP BY Title, Tickets_Purchased, Total_Price, Live_Status, Start_date
                     ORDER BY Start_date DESC LIMIT 10''', (user_id,))
    ticket_history = dbcursor.fetchall()




    # Card 7: Upcoming Events (SYSTEM_WIDE)
    dbcursor.execute('''SELECT title, date, image
                     FROM Event_Cards
                     WHERE date >= CURDATE()
                     ORDER BY date ASC LIMIT 5''')
    upcoming_events = dbcursor.fetchall()
    # Convert date to strings for Jinja
    for ev in upcoming_events:
        ev['date'] = str(ev['date'])



    # Card 8: Waiting List

    dbcursor.execute('''SELECT e.Title, DATE(e.Start_date) AS date
                        FROM Waiting_list w
                        JOIN Events e on w.Event_ID = e.Event_ID
                        WHERE w.User_ID = %s
                        AND e.Start_date >= CURDATE()              
                        ORDER BY e.Start_date ASC''', (user_id,)) # only show upcoming events in waiting list
    waiting_list = dbcursor.fetchall()
    for w in waiting_list:
        w['date'] = str(w['date']) # convert to strings for Jinja


    # Card 9: Achievement Badges
    dbcursor.execute('''SELECT a.Achievement_name, a.Description, a.Icon_class
                     FROM User_Achievements ua
                     JOIN Achievements a ON ua.Achievement_ID = a.Achievement_ID
                     WHERE ua.User_ID = %s''', (user_id,))
    achievements = dbcursor.fetchall()


    dbcursor.close()
    conn.close()

    # Render dashboard template with all the fetched data
    return render_template('dashboard.html',
                           profile=user_profile,
                           events_booked=total_booked,
                           wallet_balance=wallet_balance,
                           spent_90_days=spent_90_days,
                           has_spending_activity=has_spending_activity,
                           chart_labels=chart_labels,
                           chart_values=chart_values,
                           ticket_history=ticket_history,
                           upcoming_events=upcoming_events,
                           waiting_list=waiting_list,
                           achievements=achievements)


# POST ROUTES for Dashboard Modals

# update profile
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorised'})
    
    first_name = request.form.get('first_name', '').strip()
    last_name= request.form.get('last_name', '').strip()
    username = request.form.get('username', '').strip()
    phone = request.form.get('phone_number', '').strip()
    avatar_url = request.form.get('avatar_url', '').strip()

    conn = dbfunc.getConnection()
    dbcursor = conn.cursor()


    # Check if username and user_id exists
    dbcursor.execute('SELECT User_ID FROM Users WHERE Username = %s AND User_ID = %s', (username, session['user_id']))
    if dbcursor.fetchone():     # If record found, return in use error
        return jsonify({'success': False, 'message': 'Username already in use by another account.'})
    
    dbcursor.execute('''UPDATE Users
                     SET First_name = %s, Last_name = %s, Username = %s, Phone_Number = %s, Avatar_URL = %s
                     WHERE User_ID = %s''', (first_name, last_name, username, phone, avatar_url, session['user_id']))
    conn.commit()
    dbcursor.close()
    conn.close()

    return jsonify({'success': True, 'message': 'Profile updated successfully!'})

# Delete Account
@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorised'})
    
    conn = dbfunc.getConnection()
    dbcursor = conn.cursor()

    # Verify email and password 
    dbcursor.execute('SELECT Email, Password_hash FROM Users WHERE User_ID = %s', (session['user_id'],))
    user = dbcursor.fetchone()

    # Safely delete account and all associated data
    # To avoid foreign key constraint errors, deletion is done bottom-up (child to parent)
    try:
        dbcursor.execute('DELETE FROM Transactions WHERE User_ID = %s', (session['user_id'],))
        dbcursor.execute('DELETE FROM Waiting_list WHERE User_ID = %s', (session['user_id'],))
        dbcursor.execute('DELETE FROM Bookmarks WHERE User_ID = %s', (session['user_id'],))
        dbcursor.execute('DELETE FROM User_Achievements WHERE User_ID = %s', (session['user_id'],))
        dbcursor.execute('DELETE FROM Social_Auth WHERE User_ID = %s', (session['user_id'],))
        dbcursor.execute('DELETE FROM Sessions WHERE User_ID = %s', (session['user_id'],))

        # Find bookings for user to delete associated tickets and days
        dbcursor.execute('SELECT Booking_ID FROM Bookings WHERE User_ID = %s', (session['user_id'],))
        user_bookings = dbcursor.fetchall()
        for b in user_bookings:
            dbcursor.execute('DELETE FROM Tickets WHERE Booking_ID = %s', (b['Booking_ID'],))
            dbcursor.execute('DELETE FROM Booking_Days WHERE Booking_ID = %s', (b['Booking_ID'],))

        # Delte bookings after associated data is deleted
        dbcursor.execute('DELETE FROM Bookings WHERE User_ID = %s', (session['user_id'],))

        # Delete user and clear session
        dbcursor.execute('DELETE FROM Users WHERE User_ID = %s', (session['user_id'],))
        conn.commit()

        session.clear() # Logs out user

        return jsonify({'success': True, 'message': 'Account deleted successfully. Redirecting...'})
    
    except Exception as e:
        conn.rollback() # Rollback transaction if any error occurs during deletion
        return jsonify({'success': False, 'message': f'An error occurred while deletion. {e}'})
    finally:
        dbcursor.close()
        conn.close()


        

# Change Password
@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorised'})
    
    # Get form fields
    current_pass = request.form.get('current_password')
    new_pass = request.form.get('new_password')
    confirm_pass = request.form.get('confirm_password')

    # Check if new passwords match
    if new_pass != confirm_pass:
        return jsonify({'success': False, 'message': 'New passwords do not match.'})
    
    conn = dbfunc.getConnection()
    dbcursor = conn.cursor()

    # Select user's password_hash and check if they match
    dbcursor.execute('SELECT Password_hash FROM Users WHERE User_ID = %s', (session['user_id'],))
    user = dbcursor.fetchone()

    if not check_password_hash(user['Password_hash'], current_pass):
        return jsonify({'success': False, 'message': 'Current password is incorrect.'})
    
    new_hash = generate_password_hash(new_pass)
    dbcursor.execute('UPDATE Users SET Password_hash = %s WHERE User_ID = %s', (new_hash, session['user_id']))
    conn.commit()
    dbcursor.close()
    conn.close()

    return jsonify({'success': True, 'message': 'Password changed successfully!'})


# Add Money modal
@app.route('/add_money', methods=['POST'])
def add_money():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorised'})
    
    amount = float(request.form.get('amount', 0))
    if amount <= 0:
        return jsonify({'success': False, 'message': 'Amount must be greater than zero'})
    elif amount > 300:
        return jsonify({'success': False, 'message': 'Amount exceeds maximum limit of £300'})
    
    conn = dbfunc.getConnection()
    dbcursor = conn.cursor()

    dbcursor.execute('''INSERT INTO Transactions
                     (User_ID, Amount, Payment_method)
                     VALUES (%s, %s, %s)''', (session['user_id'], amount, 'Wallet'))
    conn.commit()
    dbcursor.close()
    conn.close()

    return jsonify({'success': True, 'message': f'£{amount:.2f} added to your wallet!'})

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
        