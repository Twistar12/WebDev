from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify, make_response
import mysql.connector, dbfunc, sys, csv
from mysql.connector import errorcode
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from io import StringIO


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
    dbcursor.execute('''SELECT  e.Event_ID, e.Title, v.Name as Venue, e.Start_date, SUM(ed.Day_Capacity) AS Total_Capacity
                     FROM Events e
                     JOIN Venues v on e.Venue_ID = v.Venue_ID
                     JOIN Event_Days ed on e.Event_ID = ed.Event_ID
                     GROUP BY e.Event_ID, e.Title, v.Name, e.Start_date
                     ORDER BY e.Start_date ASC''')
    all_events = dbcursor.fetchall()

    # Fetch venues for creating event
    dbcursor.execute('SELECT Venue_ID, Name FROM Venues ORDER BY Name ASC')
    all_venues = dbcursor.fetchall()

    # Fetch categories for creating event
    dbcursor.execute('SELECT Category_ID, Category_name FROM Categories ORDER BY Category_name ASC')
    all_categories = dbcursor.fetchall()

    dbcursor.close()
    conn.close()

    return render_template('admin_portal.html', all_users=all_users, all_events=all_events, all_venues=all_venues, all_categories=all_categories)


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


# Create Event (admin only)
@app.route('/admin/create_event', methods=['POST'])
def create_event():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorised', 'redirect': url_for('dashboard')})
    
    # Get form fields
    title = request.form.get('title', '').strip()
    venue_id = request.form.get('venue_id')
    category_id = request.form.get('category_id')
    description = request.form.get('description', '').strip()
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    price = request.form.get('price')
    capacity = request.form.get('capacity')
    
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
    start_datetime = f"{start_date_only} {start_time}"
    end_datetime = f"{end_date_only} {end_time}"


    conn = dbfunc.getConnection()
    dbcursor = conn.cursor()

    try:
        dbcursor.execute('''INSERT INTO Events (Venue_ID, Category_ID, Title, Description, Start_date, End_date, Price, Accessibility_flag)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, 1)''', (venue_id, category_id, title, description, start_datetime, end_datetime, price))

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




@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
        