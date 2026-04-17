from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify, make_response
import mysql.connector, dbfunc, sys, csv, os
from mysql.connector import errorcode
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from io import StringIO
import random, string


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
    dbcursor.execute('SELECT ec.*, e.Start_date AS full_start, e.End_date AS full_end FROM Event_Cards ec JOIN Events e ON ec.event_id = e.Event_ID ORDER BY e.Start_date ASC')
    fetched_events = dbcursor.fetchall()

    for ev in fetched_events:
        ev['date'] = str(ev['full_start']) if ev['full_start'] else "" # Use full datetime for precision
        ev['end_date'] = str(ev['full_end']) if ev['full_end'] else "" # Use full datetime for precision

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

        final_avatar = 'default_avatar.png' # default avatar if none provided or upload fails
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file.filename != '':
                filename = secure_filename(file.filename)
                save_path = os.path.join(app.root_path, 'static', 'img', 'avatars', filename)
                file.save(save_path)
                final_avatar = filename


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
            dbcursor.execute(query, (username, first_name, last_name, email, hashed_password, phone_number, final_avatar, 1))
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
            session['avatar_url'] = user.get('Avatar_URL', 'default_avatar.png') # Store avatar URL in session for easy access across site, default if not set

            if is_ajax:
                return jsonify({'success': True, 'message': 'Login successful', 'redirect': url_for('dashboard')}) # data.success hold result, data.message holds message in AJAX response
            
            # Fallback for non-AJAX login
            flash('Login successful! Welcome back, {}.'.format(user['First_name']), 'success')
            return redirect(url_for('dashboard')) # change to dashboard later when implemented
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



    # Card 6: Tickets Purchased
    # This page will only show booking ref, event.Title, tickets_purchased, total_price
    # Clicking on the card will redirect to separate tickets.html

    dbcursor.execute('''SELECT b.Booking_ID, e.Title, b.Tickets_Purchased, 
                        b.Ticket_Price AS Total_Price, 
                        e.Start_date
                     FROM Bookings b
                     JOIN Events e ON b.Event_ID = e.Event_ID
                     WHERE b.User_ID = %s
                     ORDER BY e.Start_date DESC''', (user_id,))
    ticket_history = dbcursor.fetchall()
    
    # Process ticket history to add hash ref and dummy live status for styling
    for t in ticket_history:
        # Use pseudo-random seeded with Booking_ID instead of hash to avoid small ints returning themselves
        t['Ref_No'] = f"{random.Random(t['Booking_ID']).randint(0, 0xffffff):06X}"
        # Determine status roughly
        t['Live_Status'] = 'Valid' if t['Start_date'] >= datetime.now() else 'Expired'




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
    dbcursor.execute('''SELECT wl.Event_ID, e.Title, DATE_FORMAT(e.Start_date, '%d %b %Y') AS date,
                     (SUM(ed.Day_Capacity) - COALESCE (
                        (SELECT SUM(Tickets_Purchased) FROM User_Ticket_Info WHERE Title = e.Title), 0)) AS Available_Slots
                    FROM Waiting_list wl
                    JOIN Events e on wl.Event_ID = e.Event_ID
                    JOIN Event_Days ed on e.Event_ID = ed.Event_ID
                    WHERE wl.User_ID = %s AND e.Start_date >= CURDATE()
                    GROUP BY wl.Event_ID, e.Title, e.Start_date       
                    ORDER BY e.Start_date ASC''', (session['user_id'],)) # only show upcoming events in waiting list
    waiting_list = dbcursor.fetchall()
    for w in waiting_list:
        w['date'] = str(w['date']) # convert to strings for Jinja


    # Card 9: Achievement Badges
    dbcursor.execute('''SELECT a.Achievement_name, a.Description, a.Icon_class
                     FROM User_Achievements ua
                     JOIN Achievements a ON ua.Achievement_ID = a.Achievement_ID
                     WHERE ua.User_ID = %s''', (user_id,))
    achievements = dbcursor.fetchall()

    # Admin card fetch details (only show if user is admin)
    admin_stats = {}
    if session.get('role') == 'admin':
        # Caluclate total Revenue (abs sum of all negative transactions)
        dbcursor.execute('SELECT ABS(SUM(Amount)) AS Revenue FROM Transactions WHERE Amount < 0')
        rev = dbcursor.fetchone()['Revenue']
        admin_stats['revenue'] = float(rev) if rev else 0.00

        # Calculate total users
        dbcursor.execute('SELECT COUNT(*) AS Total_Users FROM Users')
        users = dbcursor.fetchone()['Total_Users']
        admin_stats['total_users'] = users if users else 0.00

        # Count current active events
        dbcursor.execute('SELECT COUNT(*) AS Total_Events FROM Events WHERE Start_date >= CURDATE()')
        events = dbcursor.fetchone()['Total_Events']
        admin_stats['active_events'] = events if events else 0.00


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
                           achievements=achievements,
                           admin_stats=admin_stats)


# POST ROUTES for Dashboard Modals

@app.route('/add_to_waitlist', methods=['POST'])
def add_to_waitlist():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorised'})
    
    data = request.get_json()
    event_id = data.get('event_id')
    user_id = session['user_id']

    conn = dbfunc.getConnection()
    dbcursor = conn.cursor()

    try:
        # Check if user is already on waiting list for this event
        dbcursor.execute('SELECT * FROM Waiting_list WHERE User_ID = %s AND Event_ID = %s', (user_id, event_id))
        if dbcursor.fetchone():
            return jsonify({'success': False, 'message': 'You are already on the waiting list for this event.'})

        # Add user to waiting list
        dbcursor.execute('INSERT INTO Waiting_list (User_ID, Event_ID) VALUES (%s, %s)', (user_id, event_id))
        conn.commit()
        return jsonify({'success': True, 'message': 'You have been added to the waiting list for this event!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'An error occurred while adding to waiting list. {e}'})
    finally:
        dbcursor.close()
        conn.close()


# update profile
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorised'})
    
    first_name = request.form.get('first_name', '').strip()
    last_name= request.form.get('last_name', '').strip()
    username = request.form.get('username', '').strip()
    phone = request.form.get('phone_number', '').strip()
    
    old_avatar = request.form.get('current_avatar', 'default_avatar.png')
    final_avatar = old_avatar # default to old avatar if no new image uploaded
    remove_avatar = request.form.get('remove_avatar') == 'on' # checkbox value will be 'on' if checked, None if not

    if remove_avatar:
        final_avatar = 'default_avatar.png' # Set to default avatar if user chooses to remove
        if old_avatar and old_avatar != 'default_avatar.png':
            old_avatar_path = os.path.join(app.root_path, 'static', 'img', 'avatars', old_avatar)
            if os.path.exists(old_avatar_path):
                os.remove(old_avatar_path) # Remove old avatar file from server if it exists and is not default
    else: 
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.root_path, 'static', 'img', 'avatars', filename))
                final_avatar = filename

                # Delete old avatar file
                if old_avatar and old_avatar != 'default_avatar.png' and old_avatar != filename: # Only delete if old avatar exists, is not default, and is not the same as new avatar
                    old_avatar_path = os.path.join(app.root_path, 'static', 'img', 'avatars', old_avatar)
                    if os.path.exists(old_avatar_path):
                        os.remove(old_avatar_path) # Remove old avatar file from server if it exists and is not default or same as new avatar
    conn = dbfunc.getConnection()
    dbcursor = conn.cursor()


    # Check if username and user_id exists
    dbcursor.execute('SELECT User_ID FROM Users WHERE Username = %s AND User_ID != %s', (username, session['user_id']))
    if dbcursor.fetchone():     # If record found, return in use error
        return jsonify({'success': False, 'message': 'Username already in use by another account.'})
    
    dbcursor.execute('''UPDATE Users
                     SET First_name = %s, Last_name = %s, Username = %s, Phone_Number = %s, Avatar_URL = %s
                     WHERE User_ID = %s''', (first_name, last_name, username, phone, final_avatar, session['user_id']))
    conn.commit()
    dbcursor.close()
    conn.close()

    # Update session variables to reflect changes immediately on dashboard without requiring page reload
    session['username'] = username
    session['avatar_url'] = final_avatar
    session['first_name'] = first_name
    session['last_name'] = last_name
    session['phone_number'] = phone


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



@app.route('/admin_portal')
def admin_portal():
    # only access if admin is logged in, otherwise redirect to homepage
    if session.get('role') != 'admin':
        flash('Access denied. Requires admin privileges.', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = dbfunc.getConnection()
    dbcursor = conn.cursor(dictionary=True)

    # Fetch all users for User Management card
    dbcursor.execute('''SELECT User_ID, Username, First_name, Last_name, Email, Role, Join_date
                     FROM Users
                     ORDER BY Role DESC, Join_date DESC''')
    all_users = dbcursor.fetchall()

    # Fetch basic event info for Event Status Card
    dbcursor.execute('''SELECT  e.*, v.Name as Venue, c.Category_name,
                        DATE_FORMAT(e.Start_date, '%Y-%m-%d') as Start_date, DATE_FORMAT(e.Start_date, '%H:%i') as Start_time,
                        DATE_FORMAT(e.End_date, '%Y-%m-%d') as End_date, DATE_FORMAT(e.End_date, '%H:%i') as End_time,
                        e.Start_date AS full_start, e.End_date AS full_end,
                        DATEDIFF(e.Start_date, CURDATE()) AS Days_Until_Event,
                        DATEDIFF(e.End_date, CURDATE()) AS Days_After_Event,
                        (SELECT SUM(Day_Capacity) FROM Event_Days WHERE Event_ID = e.Event_ID) AS Total_Capacity,
                        (SELECT COUNT(*) FROM Tickets t JOIN Bookings b ON t.Booking_ID = b.Booking_ID WHERE b.Event_ID = e.Event_ID) AS Tickets_Sold
                     FROM Events e
                     JOIN Venues v on e.Venue_ID = v.Venue_ID
                     JOIN Event_Days ed on e.Event_ID = ed.Event_ID
                     JOIN Categories c on e.Category_ID = c.Category_ID
                     GROUP BY e.Event_ID, e.Title, v.Name, e.Start_date
                     ORDER BY e.Start_date ASC''')
    all_events = dbcursor.fetchall()

    # Process flags for event status
    now_dt = datetime.now()
    for e in all_events:
        total_capacity = float(e['Total_Capacity'] or 0) # Handle NULL values by defaulting to 0
        tickets_sold = float(e['Tickets_Sold'] or 0) # Handle NULL
        percent_sold = (tickets_sold / total_capacity * 100) if total_capacity > 0 else 0

        # Flag if <= 10 days away and < 50% sold
        e['Low_Sales_Warning'] = True if (0 <= e['Days_Until_Event'] <= 10 and percent_sold < 50) else False

        # Determine exact event status using datetime
        if e['full_end'] < now_dt:
            e['Status'] = 'past'
        elif e['full_start'] <= now_dt and e['full_end'] >= now_dt:
            e['Status'] = 'ongoing'
        elif total_capacity > 0 and tickets_sold >= total_capacity:
            e['Status'] = 'sold_out'
        else:
            e['Status'] = 'upcoming'

    # Sort events: ongoing first, then upcoming, then past
    status_priority = {'ongoing': 0, 'upcoming': 1, 'past': 2}
    all_events.sort(key=lambda x: (status_priority[x['Status']], x['Days_Until_Event']))

    # Fetch venues for creating event
    dbcursor.execute('SELECT * FROM Venues ORDER BY Name ASC')
    all_venues = dbcursor.fetchall()

    # Fetch categories for creating event
    dbcursor.execute('SELECT Category_ID, Category_name FROM Categories ORDER BY Category_name ASC')
    all_categories = dbcursor.fetchall()

    now = datetime.now()

    dbcursor.close()
    conn.close()

    return render_template('admin_portal.html', current_time=now, all_users=all_users, all_events=all_events, all_venues=all_venues, all_categories=all_categories)


# Update user (admin only version)
@app.route('/admin_update_user', methods=['POST'])
def admin_update_user():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorised'})
    
    target_user_id = int(request.form.get('user_id'))
    current_user_id = int(session['user_id']) # to prevent admins from accidentally demoting themselves, add check 

    first_name = request.form.get('first_name', '').strip()
    last_name= request.form.get('last_name', '').strip()
    role = request.form.get('role', '').strip()

    # prevent admin from changin their own role to user
    if target_user_id == current_user_id and role != 'admin':
        return jsonify({'success': False, 'message': 'Action Denied: Cannot change your own admin role. Please contact another admin to make this change.'})
    
    conn = dbfunc.getConnection()
    dbcursor = conn.cursor()
    dbcursor.execute('''UPDATE Users
                     SET First_name = %s, Last_name = %s, Role = %s
                     WHERE User_ID = %s''', (first_name, last_name, role, target_user_id))
    conn.commit()
    dbcursor.close()
    conn.close()

    return jsonify({'success': True, 'message': 'User updated successfully!', 'user_id': target_user_id, 'first_name': first_name, 'last_name': last_name, 'role': role})


# Generate CSV Reports
@app.route('/admin/generate_report', methods=['POST'])
def generate_report():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorised', 'redirect': url_for('dashboard')})
    
    report_type = request.form.get('report_type')

    conn = dbfunc.getConnection()
    dbcursor = conn.cursor()

    # Create in memory string buffer to store the CSV data
    # then use csv.writer to write data to buffer and return as response with appropriate headers

    si = StringIO()
    cw = csv.writer(si)

    # Profit by event report
    if report_type == 'profit_by_event':
        dbcursor.execute('''SELECT e.Title, v.Name as Venue, e.Start_date, SUM(ABS(t.Amount)) as Total_Revenue
                         FROM Events e
                         JOIN Bookings b ON e.Event_ID = b.Event_ID
                         JOIN Transactions t ON b.Booking_ID = t.Booking_ID
                         JOIN Venues v on e.Venue_ID = v.Venue_ID
                         WHERE t.Amount < 0
                         GROUP BY e.Event_ID
                         ORDER BY Total_Revenue DESC''')
        data = dbcursor.fetchall()
        
        # Write headers and data to CSV
        headers = ['Event Title', 'Venue', 'Start Date', 'Total Revenue (£)']
        cw.writerow(headers)
        for row in data:
            cw.writerow([row[0], row[1], row[2].strftime('%Y-%m-%d'), row[3]])
        
        filename = 'profit_by_event_report.csv'

    # Bookings per event report
    elif report_type == 'bookings_per_event':
        dbcursor.execute('''SELECT e.Title, v.Name as Venue, e.Start_date, COUNT(DISTINCT b.Booking_ID) as Total_Bookings
                         FROM Events e
                         JOIN Bookings b ON e.Event_ID = b.Event_ID
                         JOIN Venues v on e.Venue_ID = v.Venue_ID
                         GROUP BY e.Event_ID
                         ORDER BY Total_Bookings DESC''')
        data = dbcursor.fetchall()

        # Write headers and data to CSV
        headers = ['Event Title', 'Venue', 'Start Date', 'Total Bookings']
        cw.writerow(headers)
        for row in data:
            cw.writerow([row[0], row[1], row[2].strftime('%Y-%m-%d'), row[3]])
        filename = 'bookings_per_event_report.csv'
        
    # Revenue by venue
    elif report_type == 'revenue_by_venue':
        dbcursor.execute('''SELECT v.Name as Venue, SUM(ABS(t.Amount)) as Total_Revenue
                         FROM Venues v
                         JOIN Events e ON v.Venue_ID = e.Venue_ID
                         JOIN Bookings b ON e.Event_ID = b.Event_ID
                         JOIN Transactions t ON b.Booking_ID = t.Booking_ID
                         WHERE t.Amount < 0
                         GROUP BY v.Venue_ID, v.Name''')
        data = dbcursor.fetchall()

        # Write headers and data to CSV
        headers = ['Venue', 'Total Revenue (£)']
        cw.writerow(headers)
        for row in data:
            cw.writerow([row[0], row[1]])
        filename = 'revenue_by_venue_report.csv'
    else:
        return jsonify({'success': False, 'message': 'Invalid report type selected.'})

    # Send the CSV data as a response (make_response allows us to add headers for file download)
    output = make_response(si.getvalue()) # make response object containing CSV data from string buffer
    output.headers["Content-Disposition"] = f"attachment; filename={filename}"  # header tells browser to download (attachment) file with specifed filename, inline for opening in browser
    output.headers["Content-type"] = "text/csv" # header tells browser the file type
    return output








# Add venues and categories routes (admin only)
@app.route('/admin/add_venue', methods=['POST'])
def add_venue():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorised', 'redirect': url_for('dashboard')})

    name = request.form.get('name', '').strip()
    location = request.form.get('location', '').strip()
    address = request.form.get('address', '').strip()
    venue_type = request.form.get('type', '').strip()
    capacity = request.form.get('capacity')
    description = request.form.get('description', '').strip()
    final_image_name = 'default_venue.jpg' # default image if no image uploaded

    # Check if an image file is included in the request
    if 'image_url' in request.files:
        file = request.files['image_url']
        # if filename not blank, process image
        if file.filename != '':
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.root_path, 'static', 'img', 'venue_carousel', filename) 
            file.save(save_path)
            final_image_name = filename

    conn = dbfunc.getConnection()
    dbcursor = conn.cursor()

    try:
        dbcursor.execute('''INSERT INTO Venues (Name, Location, Address, Description, Type, Max_Capacity, Image_URL)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)''', (name, location, address, description, venue_type, capacity, final_image_name))
        conn.commit()
        return jsonify({'success': True, 'message': f'Venue "{name}" added successfully!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})
    finally:
        dbcursor.close()
        conn.close()



@app.route('/admin/update_venue', methods=['POST'])
def update_venue():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorised', 'redirect': url_for('dashboard')})
    
    venue_id = request.form.get('venue_id')
    name = request.form.get('name', '').strip()
    location = request.form.get('location', '').strip()
    address = request.form.get('address', '').strip()
    venue_type = request.form.get('type', '').strip()
    new_capacity = int(request.form.get('capacity', 0))
    description = request.form.get('description', '').strip()

    old_image_name = request.form.get('current_image_url') # Get current image URL from form hidden input
    if not old_image_name or old_image_name.strip() == '':
        old_image_name = 'default_venue.jpg' # Fallback to default if current image URL is missing or blank
    final_image_name = old_image_name # Default to old image, only update if new image is uploaded
    
    
    if 'image_url' in request.files:
        file = request.files['image_url']

        # if filename isnt blank, process new image, otherwise keep current image
        if file.filename != '':
            # clean filename
            filename = secure_filename(file.filename)

            # Create path
            save_path = os.path.join(app.root_path, 'static', 'img', 'venue_carousel', filename) 

            # Save file to path
            file.save(save_path)

            # Delete old image if its not the default
            if old_image_name and old_image_name != 'default_venue.jpg' and old_image_name != filename:
                old_image_path = os.path.join(app.root_path, 'static', 'img', 'venue_carousel', old_image_name)

                # Check if old file exists on storage before attempting to delete to avoid errors, then delete
                if os.path.exists(old_image_path):
                    os.remove(old_image_path) # Delete

            # Overwrite final image url so that NEW filename goes to db
            final_image_name = filename

    conn = dbfunc.getConnection()
    dbcursor = conn.cursor(dictionary=True)

    try:
        # Venue Teardown: If capacity is being reduced, check if any events at the venue would be over capacity with the new limit before allowing update to go through
        dbcursor.execute('''SELECT Max(Capacity) as max_event_cap FROM Events
                         WHERE Venue_ID = %s AND End_date >= CURDATE()''', (venue_id,))
        res = dbcursor.fetchone()['max_event_cap']  # Get the maximum capacity of upcoming events at the venue

        if res and new_capacity < res:
            return jsonify({'success': False, 'message': f'Cannot reduce capacity to {new_capacity}: Events at this venue have bookings for a higher capacity - ({res}).'})

        dbcursor.execute('''UPDATE Venues
                            SET Name = %s, Location = %s, Address = %s, Description = %s, Type = %s, Max_Capacity = %s, Image_URL = %s
                            WHERE Venue_ID = %s''', (name, location, address, description, venue_type, new_capacity, final_image_name, venue_id))
        conn.commit()
        return jsonify({'success': True, 'message': f'Venue "{name}" updated successfully!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})
    finally:
        dbcursor.close()
        conn.close()


@app.route('/admin/delete_venue', methods=['POST'])
def delete_venue():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorised', 'redirect': url_for('dashboard')})

    venue_id = request.form.get('venue_id')
    password = request.form.get('password')

    conn = dbfunc.getConnection()
    dbcursor = conn.cursor()

    try:
        # Verify admin password before allowing deletion
        dbcursor.execute('SELECT Password_hash FROM Users WHERE User_ID = %s', (session['user_id'],))
        if not check_password_hash(dbcursor.fetchone()['Password_hash'], password):
            return jsonify({'success': False, 'message': 'Incorrect password. Venue deletion cancelled.'})

        # Get image to delete from storage later
        dbcursor.execute('SELECT Image_URL FROM Venues WHERE Venue_ID = %s', (venue_id,))
        venue_image = dbcursor.fetchone()['Image_URL']

        # get all event images at venue to delete from storage later
        dbcursor.execute('SELECT Event_ID, Image_URL FROM Events WHERE Venue_ID = %s', (venue_id,))
        events_to_delete = dbcursor.fetchall()

        # To delete venue, safely delete all events hosted at it bottom up to avoid foreign key constraint errors
        for event in events_to_delete:
            event_id = event['Event_ID']
            # # Delete associated bookings, transactions, and waitlist entries for each event at the venue
            dbcursor.execute("SELECT Booking_ID FROM Bookings WHERE Event_ID = %s", (event_id,))
            # Delete booking child records from tickets, booking_days, and transactions
            for b in dbcursor.fetchall():
                dbcursor.execute("DELETE FROM Tickets WHERE Booking_ID = %s", (b['Booking_ID'],))
                dbcursor.execute("DELETE FROM Booking_Days WHERE Booking_ID = %s", (b['Booking_ID'],))
                dbcursor.execute("DELETE FROM Transactions WHERE Booking_ID = %s", (b['Booking_ID'],))

            dbcursor.execute("DELETE FROM Bookings WHERE Event_ID = %s", (event_id,))
            dbcursor.execute("DELETE FROM Waiting_List WHERE Event_ID = %s", (event_id,))
            dbcursor.execute("DELETE FROM Bookmarks WHERE Event_ID = %s", (event_id,))
            dbcursor.execute("DELETE FROM Event_Days WHERE Event_ID = %s", (event_id,))
            dbcursor.execute("DELETE FROM Events WHERE Event_ID = %s", (event_id,))

            # Remove event image
            event_image = event['Image_URL']
            if event_image and event_image != 'default_event.jpg':
                event_image_path = os.path.join(app.root_path, 'static', 'img', 'event_cards', event_image)
                if os.path.exists(event_image_path):
                    os.remove(event_image_path)
        
        # Finally, delete venue
        dbcursor.execute("DELETE FROM Venues WHERE Venue_ID = %s", (venue_id,))

        # Remove venue image
        if venue_image and venue_image != 'default_venue.jpg':
            venue_image_path = os.path.join(app.root_path, 'static', 'img', 'venue_carousel', venue_image)
            if os.path.exists(venue_image_path):
                os.remove(venue_image_path)
        conn.commit()
        return jsonify({'success': True, 'message': 'Venue and all associated events deleted successfully!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})
    finally:
        dbcursor.close()
        conn.close()




# Create Event (admin only)
@app.route('/admin/add_event', methods=['POST'])
def add_event():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorised', 'redirect': url_for('dashboard')})
    
    # Get form fields
    title = request.form.get('title', '').strip()
    venue_id = request.form.get('venue_id')
    category_id = request.form.get('category_id')
    description = request.form.get('description', '').strip()
    price = request.form.get('price')
    capacity = int(request.form.get('capacity', 0))

    # time fields
    start_date_only = request.form.get('start_date')
    start_time = request.form.get('start_time')
    end_date_only = request.form.get('end_date')
    end_time = request.form.get('end_time')

    # HTML time excludes seconds, append them for SQL required format
    if len(start_time) == 5:
        start_time += ':00'
    if len(end_time) == 5:
        end_time += ':00'


    # Stich date and time for DATETIME format
    start_datetime = datetime.strptime(f"{start_date_only} {start_time}", '%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.strptime(f"{end_date_only} {end_time}", '%Y-%m-%d %H:%M:%S')

    # Prevent past dates in events
    if start_datetime < datetime.now():
        return jsonify({'success': False, 'message': 'Event start date and time cannot be in the past.'})

    if end_datetime <= start_datetime:
        return jsonify({'success': False, 'message': 'Event end date and time must be after start date and time.'})



    final_image_name = 'default_event.jpg' # default image if no image uploaded

    if 'image_url' in request.files:
        file = request.files['image_url']
        if file.filename != '':
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.root_path, 'static', 'img', 'event_cards', filename) 
            file.save(save_path)
            final_image_name = filename

    conn = dbfunc.getConnection()
    dbcursor = conn.cursor()

    try:
        # Check venue capacity to ensure event capacity does not exceed it
        dbcursor.execute('SELECT Max_Capacity FROM Venues WHERE Venue_ID = %s', (venue_id,))
        venue_capacity = dbcursor.fetchone()[0]

        if capacity > venue_capacity:
            return jsonify({'success': False, 'message': f'Event capacity ({capacity}) cannot exceed venue maximum capacity of {venue_capacity}.'})
        

        dbcursor.execute('''INSERT INTO Events (Venue_ID, Category_ID, Title, Description, Start_date, End_date, Price, Capacity, Image_URL, Accessibility_flag)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)''', (venue_id, category_id, title, description, start_datetime, end_datetime, price, capacity, final_image_name))

        event_id = dbcursor.lastrowid # Get the ID of the newly created Event_ID to insert into Event_Days

        # Convert start and end date strings to datetime objects for looping
        start_dt = datetime.strptime(start_date_only, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date_only, '%Y-%m-%d')

        # Get length of event in days to loop and insert a record for each day with same capacity
        length = end_dt - start_dt
        
        for i in range(length.days + 1): # Loop through each day of the event, including end date
            day = start_dt + timedelta(days=i) # add day according to iteration to start date
            dbcursor.execute('''INSERT INTO Event_Days (Event_ID, Date, Start_Time, End_Time, Day_Capacity)
                             VALUES (%s, %s, %s, %s, %s)''', (event_id, day.strftime('%Y-%m-%d'), start_time, end_time, capacity))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Event created successfully!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})
    finally:
        dbcursor.close()
        conn.close()



# Update Event (admin only)
@app.route('/admin/update_event', methods=['POST'])
def update_event():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorised', 'redirect': url_for('dashboard')})
    
    # Get form fields
    event_id = request.form.get('event_id')
    title = request.form.get('title', '').strip()
    venue_id = request.form.get('venue_id')
    category_id = request.form.get('category_id')
    description = request.form.get('description', '').strip()
    price = request.form.get('price')
    capacity = int(request.form.get('capacity', 0))
    acc_flag = 1 if request.form.get('accessibility_flag') else 0
    
    # time fields
    start_date_only = request.form.get('start_date')
    start_time = request.form.get('start_time')
    end_date_only = request.form.get('end_date')
    end_time = request.form.get('end_time')

    # HTML time excludes seconds, append them for SQL required format
    if len(start_time) == 5:
        start_time += ':00'
    if len(end_time) == 5:
        end_time += ':00'


    # Stich date and time for DATETIME format
    start_datetime = datetime.strptime(f"{start_date_only} {start_time}", '%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.strptime(f"{end_date_only} {end_time}", '%Y-%m-%d %H:%M:%S')

    # Prevent past dates in events
    if start_datetime < datetime.now():
        return jsonify({'success': False, 'message': 'Event start date and time cannot be in the past.'})#
    
    if end_datetime <= start_datetime:  
        return jsonify({'success': False, 'message': 'Event end date and time must be after start date and time.'})

    # Handle image upload and replacement
    old_image_name = request.form.get('current_image_url') # Get current image URL from form hidden input
    if not old_image_name or old_image_name.strip() == '':
        old_image_name = 'default_event.jpg' # Fallback to default if current image URL is missing or blank
    final_image_name = old_image_name # Default to old image, update if new upload

    if 'image_url' in request.files:
        file = request.files['image_url']
        # if filename isnt blank, process new image
        if file.filename != '':
            # clean filename
            filename = secure_filename(file.filename)
            # Create path
            save_path = os.path.join(app.root_path, 'static', 'img', 'event_cards', filename) 
            # Save file to path
            file.save(save_path)

            # Delete old image if not default and not same as new upload
            if old_image_name and old_image_name != 'default_event.jpg' and old_image_name != filename:
                old_image_path = os.path.join(app.root_path, 'static', 'img', 'event_cards', old_image_name)

                # Check if old file exists on storage before attempting to delete to avoid errors, then delete
                if os.path.exists(old_image_path):
                    os.remove(old_image_path) # Delete

            # Overwrite final image url so that NEW filename goes to db
            final_image_name = filename

    conn = dbfunc.getConnection()
    dbcursor = conn.cursor()

    try:
        # Check venue capacity to ensure event capacity does not exceed it
        dbcursor.execute('SELECT Max_Capacity FROM Venues WHERE Venue_ID = %s', (venue_id,))
        venue_capacity = dbcursor.fetchone()[0]
        if capacity > venue_capacity:
            return jsonify({'success': False, 'message': f'Event capacity ({capacity}) cannot exceed venue maximum capacity of {venue_capacity}.'})

        # Check if event has existing bookings, if so prevent reducing capacity below tickets already sold
        dbcursor.execute('''SELECT COUNT(*) as sold FROM Tickets t
                            JOIN Bookings b ON t.Booking_ID = b.Booking_ID
                            WHERE b.Event_ID = %s''', (event_id,))
        tickets_sold = dbcursor.fetchone()[0]
        if capacity < tickets_sold:
            return jsonify({'success': False, 'message': f'Event capacity cannot be reduced below the number of tickets already sold ({tickets_sold}).'})
        
        # Update event details in Events table
        dbcursor.execute('''UPDATE Events
                         SET Venue_ID=%s, Category_ID=%s, Title=%s, Description=%s, Start_date=%s, End_date=%s, Price=%s, Capacity=%s, Image_URL=%s, Accessibility_flag=%s
                         WHERE Event_ID=%s''', (venue_id, category_id, title, description, start_datetime, end_datetime, price, capacity, final_image_name, acc_flag, event_id))

        # Handle date changes by deleting old event days and inserting new ones based on updated start and end dates
        dbcursor.execute('DELETE FROM Event_Days WHERE Event_ID = %s', (event_id,)) # Delete old event days
        # Recalculate event length 
        start_dt = datetime.strptime(start_date_only, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date_only, '%Y-%m-%d')
        length = end_dt - start_dt

        for i in range(length.days + 1):
            day = start_dt + timedelta(days=i)
            dbcursor.execute('''INSERT INTO Event_Days (Event_ID, Date, Start_Time, End_Time, Day_Capacity)
                             VALUES (%s, %s, %s, %s, %s)''', (event_id, day.strftime('%Y-%m-%d'), start_time, end_time, capacity))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Event updated successfully!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})
    finally:
        dbcursor.close()
        conn.close()

    
# Delete Event (admin only)
@app.route('/admin/delete_event', methods=['POST'])
def delete_event():
    if session.get('role') != 'admin': return jsonify({'success': False, 'message': 'Unauthorized'})
    
    event_id = request.form.get('event_id')
    
    conn = dbfunc.getConnection()
    dbcursor = conn.cursor(dictionary=True)
    
    try:
        # Get image url for later
        dbcursor.execute('SELECT Image_URL FROM Events WHERE Event_ID = %s', (event_id,))
        event_image = dbcursor.fetchone()['Image_URL']

        # all associated data deleted bottom up
        dbcursor.execute("SELECT Booking_ID FROM Bookings WHERE Event_ID = %s", (event_id,))
        
        # delete child records
        for b in dbcursor.fetchall():
            bid = b['Booking_ID']
            dbcursor.execute("DELETE FROM Tickets WHERE Booking_ID = %s", (bid,))
            dbcursor.execute("DELETE FROM Booking_Days WHERE Booking_ID = %s", (bid,))
            dbcursor.execute("DELETE FROM Transactions WHERE Booking_ID = %s", (bid,))
            
        # delete parent records after child
        dbcursor.execute("DELETE FROM Bookings WHERE Event_ID = %s", (event_id,))
        dbcursor.execute("DELETE FROM Waiting_List WHERE Event_ID = %s", (event_id,))
        dbcursor.execute("DELETE FROM Bookmarks WHERE Event_ID = %s", (event_id,))
        dbcursor.execute("DELETE FROM Event_Days WHERE Event_ID = %s", (event_id,))
        
        # Delete EVENT
        dbcursor.execute("DELETE FROM Events WHERE Event_ID = %s", (event_id,))

        # Delete event image
        if event_image and event_image != 'default_event.jpg':
            event_image_path = os.path.join(app.root_path, 'static', 'img', 'event_cards', event_image)
            if os.path.exists(event_image_path):
                os.remove(event_image_path)
                
        conn.commit()
        return jsonify({'success': True, 'message': 'Event and all associated data permanently deleted!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Error deleting event: {str(e)}'})
    finally:
        dbcursor.close()
        conn.close()


@app.route('/booking/<int:event_id>')
def booking(event_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorised', 'redirect': url_for('index')})
    
    conn = dbfunc.getConnection()
    dbcursor = conn.cursor(dictionary=True)

    # Get Event and User Details
    dbcursor.execute('SELECT * FROM Events e WHERE Event_ID = %s', (event_id,))
    event = dbcursor.fetchone()

    if not event:
        return jsonify({'success': False, 'message': 'Event not found.', 'redirect': url_for('events')})
    
    dbcursor.execute('SELECT * FROM Users WHERE User_ID = %s', (session['user_id'],))
    user = dbcursor.fetchone()

    # Get Wallet Balance
    dbcursor.execute('SELECT Balance FROM Wallet_Balance WHERE User_ID = %s', (session['user_id'],))
    wallet_res = dbcursor.fetchone()
    wallet_balance = float(wallet_res['Balance']) if wallet_res and wallet_res['Balance'] is not None else 0.00

    # Get event days 
    dbcursor.execute('SELECT Day_ID, Date, Day_Capacity FROM Event_Days WHERE Event_ID = %s ORDER BY Date ASC', (event_id,))
    event_days = dbcursor.fetchall()

    dbcursor.close()
    conn.close()

    # Calculate Discount Percentage based on advanced booking
    days_in_advance = (event['Start_date'].date() - datetime.now().date()).days
    disc_percent = 0
    if days_in_advance >= 50:
        disc_percent = 20
    elif days_in_advance >= 35:
        disc_percent = 15
    elif days_in_advance >= 25:
        disc_percent = 10
    elif days_in_advance >= 15:
        disc_percent = 5

    # Current exact time
    now = datetime.now()

    # Render the booking page with the retrieved data
    return render_template('booking.html', event=event, event_days=event_days, user=user, wallet_balance=wallet_balance, disc_percent=disc_percent, current_time=now)



@app.route('/process_booking', methods=['POST'])
def process_booking():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorised', 'redirect': url_for('index')})

    # Extract form data
    event_id = request.form.get('event_id')
    num_tickets = int(request.form.get('num_tickets', 1))
    selected_days = request.form.getlist('selected_days') # Returns list of dates
    is_student = 1 if request.form.get('student_discount') == 'on' else 0
    payment_method = request.form.get('payment')
    
    if not selected_days or num_tickets < 1 or num_tickets > 10:
        return jsonify({'success': False, 'message': 'Please select valid number of tickets and at least one day.'})
    
    conn = dbfunc.getConnection()
    dbcursor = conn.cursor(dictionary=True)

    try: 
        # Server side price calculation
        dbcursor.execute('SELECT Title, Price, Start_date FROM Events WHERE Event_ID = %s', (event_id,))
        event = dbcursor.fetchone()

        base_price_per_day = float(event['Price'])
        total_base = base_price_per_day * num_tickets * len(selected_days)

        # Calculate discount based on advanced booking
        days_in_advance = (event['Start_date'].date() - datetime.now().date()).days
        disc_percent = 0
        if days_in_advance >= 50:
            disc_percent = 20
        elif days_in_advance >= 35:
            disc_percent = 15
        elif days_in_advance >= 25:
            disc_percent = 10
        elif days_in_advance >= 15:
            disc_percent = 5

        advanced_disc = total_base * (disc_percent / 100)
        student_amount = (total_base - advanced_disc) * 0.10 if is_student else 0

        final_price = total_base - advanced_disc - student_amount

        discounted_price = total_base - final_price # Calculate total discount amount for receipt

        # Wallet Validation if wallet selected
        if payment_method == 'wallet':
            dbcursor.execute('SELECT Balance FROM Wallet_Balance WHERE User_ID = %s', (session['user_id'],))
            wallet_res = dbcursor.fetchone()
            balance = float(wallet_res['Balance']) if wallet_res and wallet_res['Balance'] is not None else 0.00
            
            if balance < final_price:
                return jsonify({'success': False, 'message': 'Insufficient wallet balance. Please choose another payment method or add funds to your wallet.'})
            
        # Process DB inserts
        # Insert booking record
        dbcursor.execute('''INSERT INTO Bookings (User_ID, Event_ID, Booking_date,
                         Tickets_Purchased, Ticket_Price, Booking_Status,
                         Original_Price, Discount_Applied, Is_Student)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                         (session['user_id'], event_id, datetime.now(),
                          num_tickets, final_price, 'Success',
                          total_base, discounted_price, is_student))

        booking_id = dbcursor.lastrowid # Get the ID of the newly created Booking_ID to insert into Tickets and Booking_Days
        
        # Insert booking days records
        # # Selcted the days from event_days table to get the corresponding Day_IDs for the selected dates to insert into Booking_Days
        # dbcursor.execute('''SELECT Day_ID, Date FROM Event_Days
        #                  WHERE Event_ID = %s
        #                  ORDER BY Date ASC''', (event_id,))
        # event_days = dbcursor.fetchall()

        for day_id in selected_days:
            if day_id and str(day_id).strip() != '': # validate day_id to prevent blank entries
                dbcursor.execute('''INSERT INTO Booking_Days (Booking_ID, Day_ID)
                                VALUES (%s, %s)''', (booking_id, day_id))
            else:
                return jsonify({'success': False, 'message': 'Invalid day selection. Please try again.'})
            
        # Insert Transaction
        dbcursor.execute('''INSERT INTO Transactions (User_ID, Booking_ID, Amount, Payment_method, Transaction_date)
                         VALUES (%s, %s, %s, %s, %s)''', (session['user_id'], booking_id, -final_price, payment_method, datetime.now()))

        # Generate Tickets
        generated_tickets = []
        for _ in range(num_tickets):
            # Format: FIRST3LETTERS OF EVENT + RANDOM 4 ALPHANUMERALS + Pseudo-Random Booking_ID mapping
            code = f"{event['Title'][:3].upper()}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}-{random.Random(booking_id).randint(0, 0xffff):04X}" # Seed with booking_id and take hex digits for uniqueness without exposing actual ID
            # default to valid status and insert activation time later when user activates ticket
            dbcursor.execute('''INSERT INTO Tickets (Booking_ID, Code, Ticket_Status)
                             VALUES (%s, %s, %s)''', (booking_id, code, 'Valid'))
            generated_tickets.append(code)

        conn.commit()

        # return receipt data
        return jsonify({'success': True,
                            'receipt': {
                                'ref_no': f"{random.Random(booking_id).randint(0, 0xffffff):06X}",
                                'base': f"£{total_base:.2f}",
                                'advanced_disc': f"£{advanced_disc:.2f}" if advanced_disc > 0 else "£0.00",
                                'student_disc': f"£{student_amount:.2f}" if student_amount > 0 else "£0.00",
                                'final': f"£{final_price:.2f}",
                                'tickets': generated_tickets,
                            }})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Error processing booking: {str(e)}'})
    finally:
        dbcursor.close()
        conn.close()


@app.route('/tickets')
def tickets():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorised', 'redirect': url_for('index')})
    
    conn = dbfunc.getConnection()
    dbcursor = conn.cursor(dictionary=True)

    try: 
        # Query VIEW User_ticket_info and join tickets and events with it
        dbcursor.execute('''
            SELECT 
                uti.*,
                t.Ticket_ID,
                b.Booking_ID,
                (CASE
                    WHEN (t.Ticket_Status = 'Cancelled') THEN 'Cancelled'
                    WHEN (TIMESTAMPDIFF(SECOND, e.End_date, NOW()) >= 1) THEN 'Expired'
                    WHEN (TIMESTAMPDIFF(MINUTE, t.Activated_Time, NOW()) >= 10) THEN 'Used'
                    WHEN (t.Activated_Time IS NOT NULL) THEN 'Active'
                    WHEN (t.Activated_Time IS NULL) THEN 'Valid'
                    ELSE 'Valid'
                END) AS Live_Status,
                (SELECT GROUP_CONCAT(ed.Date ORDER BY ed.Date ASC SEPARATOR ', ')
                 FROM Booking_Days bd
                 JOIN Event_Days ed ON bd.Day_ID = ed.Day_ID
                 WHERE bd.Booking_ID = b.Booking_ID) AS Booked_Dates,
                (SELECT TIME_FORMAT(MIN(ed.Start_Time), '%H:%i')
                 FROM Booking_Days bd
                 JOIN Event_Days ed ON bd.Day_ID = ed.Day_ID
                 WHERE bd.Booking_ID = b.Booking_ID) AS Start_time,
                (SELECT TIME_FORMAT(MAX(ed.End_Time), '%H:%i')
                 FROM Booking_Days bd
                 JOIN Event_Days ed ON bd.Day_ID = ed.Day_ID
                 WHERE bd.Booking_ID = b.Booking_ID) AS End_time
            FROM user_ticket_info uti
            JOIN Tickets t ON uti.Code = t.Code
            JOIN Bookings b ON t.Booking_ID = b.Booking_ID
            JOIN Events e ON b.Event_ID = e.Event_ID
            WHERE uti.User_ID = %s
            ORDER BY e.Start_date ASC
        ''', (session['user_id'],))

        raw_tickets = dbcursor.fetchall()

        # Group tickets by Booking_ID
        grouped_bookings = {}
        for t in raw_tickets:
            bid = t['Booking_ID']
            if bid not in grouped_bookings:
                grouped_bookings[bid] = {
                    'Booking_ID': bid,
                    'Title': t['Title'],
                    'Venue': t['Venue'],
                    'Booked_Dates': t['Booked_Dates'],
                    'Start_time': t['Start_time'],
                    'End_time': t['End_time'],
                    'Tickets': []
                }
            
            # Format time into strings (HH:MM) roughly like before just in case
            if t['Start_time'] and not isinstance(t['Start_time'], str):
                 t['Start_time'] = str(t['Start_time'])[:-5]
            if t['End_time'] and not isinstance(t['End_time'], str):
                 t['End_time'] = str(t['End_time'])[:-5]
                 
            grouped_bookings[bid]['Tickets'].append({
                'Ticket_ID': t['Ticket_ID'],
                'Code': t['Code'],
                'Live_Status': t['Live_Status']
            })

        return render_template('tickets.html', grouped_bookings=grouped_bookings.values())
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching tickets: {str(e)}'})
    finally:
        dbcursor.close()
        conn.close()


@app.route('/activate_ticket', methods=['POST'])
def activate_ticket():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorised', 'redirect': url_for('index')})
    
    ticket_id = request.form.get('ticket_id')

    conn = dbfunc.getConnection()
    dbcursor = conn.cursor()

    try:
        # Update Activated_Time to current time to mark as active
        dbcursor.execute('''UPDATE Tickets
                         SET Activated_Time = NOW()
                         WHERE Ticket_ID = %s AND Booking_ID IN (
                         SELECT Booking_ID FROM Bookings
                         WHERE User_ID = %s)
                         AND Activated_Time IS NULL''', (ticket_id, session['user_id']))
        conn.commit()
        
        # if dbcursor.rowcount == 0:
        #     return jsonify({'success': False, 'message': 'Ticket is already activated or invalid.'})
        return jsonify({'success': True, 'message': 'Ticket activated successfully!'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Error activating ticket: {str(e)}'})
    finally:
        dbcursor.close()
        conn.close()


@app.route('/cancel_ticket', methods=['POST'])
def cancel_ticket():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorised', 'redirect': url_for('index')})

    ticket_id = request.form.get('ticket_id')

    conn = dbfunc.getConnection()
    dbcursor = conn.cursor()

    try:
        # Update Ticket_Status to 'Cancelled'
        # Permanently trigger 'Cancelled' in CASE statement
        dbcursor.execute('''UPDATE Tickets
                         SET Ticket_Status = 'Cancelled'
                         WHERE Ticket_ID = %s AND Booking_ID IN (
                         SELECT Booking_ID FROM Bookings
                         WHERE User_ID = %s)
                         AND Ticket_Status != 'Cancelled';''', (ticket_id, session['user_id']))
        conn.commit()

        return jsonify({'success': True, 'message': 'Ticket cancelled successfully!'})

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Error cancelling ticket: {str(e)}'})
    finally:
        dbcursor.close()
        conn.close()


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
        