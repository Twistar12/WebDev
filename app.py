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


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
        