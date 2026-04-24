<!-- Student Name: Alvin Vellappallil -->
<!-- Student ID: 24028338 -->

# Bristol Community Events

A full-stack web application for discovering, booking, and managing events in Bristol. Users can browse events, make bookings with flexible pricing, manage tickets, and download booking receipts as PDFs.

## Project Overview

**Bristol Community Events** is built with Flask (Python backend) and MySQL for data persistence. It provides:
- Event discovery and filtering (by venue, price, date, category, accessibility)
- Secure user authentication and profiles
- Multi-day event bookings with dynamic pricing
- Ticket generation and QR code management
- Wallet-based payment system
- PDF receipt downloads for bookings
- Admin portal for event and booking management
- Waiting list system for sold-out events
- Lazy-loaded images for optimized performance

---

## File Structure

```
WebDev/
├── app.py                 # Main Flask application
├── dbfunc.py             # Database connection utilities
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── static/
│   ├── css/
│   │   └── index.css    # Custom styles
│   └── img/             # Images (event cards, carousels, avatars)
└── templates/
    ├── base.html        # Base template with nav/footer
    ├── index.html       # Home page with carousel
    ├── events.html      # Event discovery & filtering
    ├── booking.html     # Booking form & receipt modal
    ├── tickets.html     # Ticket management
    ├── dashboard.html   # User dashboard
    ├── admin_portal.html # Admin management interface
    ├── login.html       # Login page
    ├── sign-up.html     # Registration page
    ├── about.html       # About page
    └── ...other pages
```

---

## Dependencies

### Backend (Python)
- **Flask** 3.1.3 - Web framework
- **mysql-connector-python** 9.6.0 - MySQL database driver
- **Werkzeug** 3.1.8 - WSGI utilities and password hashing
- **Jinja2** 3.1.6 - Template engine
- **python-dateutil** 2.9.0 - Date/time utilities
- **passlib** 1.7.4 - Password hashing library
- **reportlab** 4.4.1 - PDF generation
- **python-dotenv** - Environment variable management

### Frontend
- **Bootstrap 5** - CSS framework
- **Font Awesome 6** - Icon library
- **Jinja2** - Server-side templating

### Database
- **MySQL 8.0.44+** - Relational database

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Git

### 1. Clone Repository
```bash
cd "c:\WebDevelopmentProject WIP\WebDev"
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Database
Create a `.env` file in the project root:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=bristol_events_db
FLASK_SECRET_KEY=your_random_secret_key_here
```

### 5. Initialize Database
```bash
mysql -u root -p < bristol_events_dump
```

### 6. Run the Application
```bash
python app.py
```

The app will be available at `http://localhost:5000`

---

## How to Use the App

### For Regular Users

#### 1. **Sign Up / Login**
- Navigate to `/signup` to create a new account
- Enter username, email, password, and optional profile picture
- Login at `/login` with your credentials

#### 2. **Browse Events**
- Visit the **Events** page to view all available events
- Use filters to search by:
  - **Venue** - Specific venue location
  - **Price Range** - £0-£50 slider
  - **Date Range** - Select start and end dates
  - **Category** - Music, Theatre, Sports, etc.
  - **Advanced Filters** - Venue type, accessibility features

#### 3. **Book an Event**
- Click "Book Now" on any event card
- Select number of tickets (1-10)
- Choose booking dates (for multi-day events)
- Apply student discount if eligible
- Choose payment method (Wallet, Apple Pay, Google Pay, PayPal)
- Confirm booking

#### 4. **Download Receipt (PDF)**
- After successful booking, a receipt modal appears
- Click **"Download Receipt (PDF)"** to save booking details locally
- Receipt includes reference number, pricing breakdown, and ticket codes

#### 5. **Manage Tickets**
- Visit **My Tickets** page (`/tickets`)
- View all bookings grouped by event
- Filter by status (Valid, Active, Expired, Cancelled)
- Sort by booking date
- Click ticket card to view QR code and ticket details
- Activate tickets 1 hour before event start
- Cancel tickets for refund

#### 6. **Dashboard**
- View user profile summary
- Track booking history with status
- Monitor wallet balance
- View upcoming events
- Manage waiting list entries

#### 7. **Wallet System**
- Wallet balance shown on booking page
- Top up via payment methods
- Deductions recorded for wallet payments
- Refunds credited automatically

---

### For Admin Users

#### 1. **Admin Portal** (`/admin_portal`)
- Access requires admin role

#### 2. **Event Management**
- **Create Events** - Add new events with multi-day support
- **Edit Events** - Modify event details, dates, pricing
- **Delete Events** - Remove events and associated bookings
- **View Statistics** - See tickets sold, revenue, occupancy

#### 3. **Booking Management**
- View all bookings for each event
- Cancel individual bookings with automatic refunds
- Cancel all event bookings at once
- Track booking dates and payment methods

#### 4. **Financial Reporting**
- Generate reports on bookings per event
- Track revenue by event, venue, category
- Export transaction history

---

## Test User Accounts

Use the following credentials to login and explore the application:

| Username | Email | Role | Password |
|----------|-------|------|----------|
| alice_w | alice@example.com | User | aliceWonder123 |
| bob_builder | bob@example.com | **Admin** | bobBuilder123 |
| charlie_c | charlie@example.com | User | charlieChaplin123 |
| diana_p | diana@example.com | User | dianaPrince123 |
| evan_m | evan@example.com | User | evanMcGregor123 |
| fiona_g | fiona@example.com | User | fionaGallagher123 |
| george_l | george@example.com | User | georgeLucas123 |
| hannah_m | hannah@example.com | User | hannahMontana123 |
| ian_s | ian@example.com | User | ianSomerhalder123 |
| jenna_o | jenna@example.com | User | jennaOrtega123 |
| test_user | new@example.com | User | testUser123 |
| user_name | user@example.com | User | userName123 |

**Note:** Passwords in the database are hashed using scrypt. For testing purposes, these accounts can be reset or new test accounts created via the signup form.

---


## Key Features

### Event Management
- Multi-day events with individual day capacities
- Dynamic pricing based on advance booking (5-20% discounts)
- Student discount (10% off)
- Event accessibility tracking
- Event image galleries

### Booking System
- Multi-ticket, multi-day bookings
- Price calculations with discounts
- Wallet and external payment support
- Automatic ticket code generation
- QR codes for ticket validation

### User Features
- Profile management with avatar upload
- Booking history with status tracking
- Ticket activation (1 hour before event)
- Ticket cancellation with refunds
- Waiting list for sold-out events
- Wallet balance management

### Technical Features
- Lazy-loaded carousel images for performance
- Server-side PDF generation for receipts
- Secure password hashing (scrypt)
- AJAX form submissions (no page reloads)
- Responsive Bootstrap UI
- Database views for complex queries

---

## Database Schema

### Main Tables
- **users** - User accounts and profiles
- **events** - Event details
- **event_days** - Multi-day event scheduling
- **venues** - Event venues
- **categories** - Event categories
- **bookings** - User bookings
- **tickets** - Individual ticket records
- **booking_days** - Booking-to-day associations
- **transactions** - Payment records
- **waiting_list** - Waiting list entries

### Views
- **event_cards** - Event display data
- **user_ticket_info** - Ticket details for users
- **wallet_balance** - User wallet balances
- **available_slots** - Event capacity tracking

---

## Troubleshooting

### Database Connection Issues
- Verify MySQL is running: `mysql -u root -p`
- Check `.env` file has correct credentials
- Ensure database `bristol_events_db` exists

### Python Import Errors
- Reinstall dependencies: `pip install -r requirements.txt`
- Verify virtual environment is activated

### PDF Download Not Working
- Ensure `reportlab` is installed: `pip install reportlab==4.4.1`
- Check file permissions in project directory

### Session/Login Issues
- Clear browser cookies
- Check `FLASK_SECRET_KEY` in `.env`
- Verify database connection

---

## Development Notes

- Flask debug mode can be enabled by setting `FLASK_ENV=development`
- Database changes require schema updates and migration
- Image uploads go to `static/img/` directories
- PDF receipts are generated on-the-fly and streamed to user

---

## Support & Contact

For issues or feature requests, refer to the admin portal or contact the development team.

---

**Last Updated:** April 23, 2026
**Version:** 1.0
