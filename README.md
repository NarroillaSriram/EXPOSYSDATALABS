# Exposys Data Labs - Internship & Training Management System
First Change
A full-stack web application built with Python Flask and MySQL, inspired by Exposys Data Labs.
second
## Tech Stack
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Backend**: Python Flask
- **Database**: MySQL
- **ORM**: Flask-SQLAlchemy
- **Auth**: Flask-Login + Werkzeug password hashing

## Project Structure
```
exposys_project/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── forms.py                # WTForms form classes
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── models/
│   ├── __init__.py
│   └── models.py           # SQLAlchemy models
├── routes/
│   ├── __init__.py
│   ├── main.py             # Public routes
│   ├── auth.py             # Authentication routes
│   ├── student.py          # Student dashboard routes
│   └── admin.py            # Admin dashboard routes
├── templates/
│   ├── base.html           # Base layout
│   ├── index.html          # Homepage
│   ├── about.html
│   ├── contact.html
│   ├── internships.html
│   ├── auth/               # Login/Register pages
│   ├── student/            # Student dashboard
│   ├── admin/              # Admin dashboard
│   └── errors/             # 404, 500 pages
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
├── database/
│   └── schema.sql
└── uploads/                # Payment screenshots
```

## Setup Instructions

### Step 1: Prerequisites
- Python 3.8+
- MySQL Server 8.0+
- pip

### Step 2: Clone & Navigate
```bash
cd exposys_project
```

### Step 3: Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Setup MySQL Database
Open MySQL and run:
```sql
CREATE DATABASE exposys_db;
```
Or run the schema file:
```bash
mysql -u root -p < database/schema.sql
```

### Step 6: Configure Environment
Edit `.env` file:
```
SECRET_KEY=your_secret_key_here
DB_USERNAME=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=exposys_db
ADMIN_EMAIL=111111111
ADMIN_PASSWORD=111111111
```

### Step 7: Run the Application
```bash
python app.py
```

Visit: **http://localhost:5000**

## Default Credentials

### Admin Login
- URL: http://localhost:5000/admin/login
- Email: `111111111111`
- Password: `1111111111`

### Student
- Register at: http://localhost:5000/register
- Login at: http://localhost:5000/login

## Features
- ✅ Responsive homepage with hero, domains, about, training, testimonials sections
- ✅ Student registration with full form validation
- ✅ Student login/logout with session management
- ✅ Admin login with protected dashboard
- ✅ Admin: view/search/delete students
- ✅ Admin: manage payment statuses
- ✅ Admin: view contact messages
- ✅ Admin: export students to CSV
- ✅ Payment page with QR code + screenshot upload
- ✅ Flash messages for all actions
- ✅ 404/500 error pages
- ✅ Password hashing with Werkzeug
- ✅ Mobile-responsive design

## Pages
| URL | Description |
|-----|-------------|
| `/` | Homepage |
| `/about` | About page |
| `/internships` | Internship listings |
| `/contact` | Contact form |
| `/register` | Student registration |
| `/login` | Student login |
| `/dashboard` | Student dashboard |
| `/payment` | Payment page |
| `/profile` | Student profile |
| `/admin/login` | Admin login |
| `/admin/dashboard` | Admin dashboard |
| `/admin/students` | Manage students |
| `/admin/payments` | Manage payments |
| `/admin/contacts` | View messages |
| `/admin/students/export` | Export CSV |
