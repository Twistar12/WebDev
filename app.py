from flask import Flask, render_template, request, redirect, url_for
import mysql.connector, dbfunc, sys
from mysql.connector import errorcode

app = Flask(__name__)

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
    print(venue_carousel)

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

    # Host event parameters
    venue = request.args.get('venue')
    price = request.args.get('price')
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Form SQL query from event_cards view
    query = "SELECT * FROM event_cards WHERE 1=1"
    params = []

    # Append filter conditions if provided
    if venue:
        query += " AND venue = %s"
        params.append(venue)
    if category:
        query += " AND category = %s"
        params.append(category)
    if price:
        if price == 'free':
            query += " AND price = 0"
        elif price == 'low':
            query += " AND price > 0 AND price <= 20"
        elif price == 'medium':
            query += " AND price > 20 AND price <= 50"
        elif price == 'high':
            query += " AND price > 50"

    if start_date and end_date:
        query += " AND start_date >= %s AND end_date <= %s"
        params.extend([start_date, end_date])
    elif start_date:
        query += " AND start_date >= %s"
        params.append(start_date)
    elif end_date:
        query += " AND end_date <= %s"
        params.append(end_date)

    query += " ORDER BY start_date ASC"

    # Execute query with parameters
    dbcursor.execute(query, tuple(params))
    events = dbcursor.fetchall()

    # fetch dropdown options dynamically to stay up to date with database
    dbcursor.execute('SELECT DISTINCT venue FROM Event_Cards WHERE venue IS NOT NULL ORDER BY venue ASC')
    venues = [row['venue'] for row in dbcursor.fetchall()]

    dbcursor.execute('SELECT DISTINCT category FROM Event_Cards WHERE category IS NOT NULL ORDER BY category ASC')
    categories = [row['category'] for row in dbcursor.fetchall()]

    dbcursor.close()
    conn.close()

    return render_template('events.html', events=events, venues=venues, categories=categories)

if __name__ == '__main__':
    app.run(debug=True)
        