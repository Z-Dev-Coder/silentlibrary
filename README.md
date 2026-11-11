# Silent Library — Full-Stack Library Management System (LMS)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-092E20.svg)](https://www.djangoproject.com/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57.svg)](https://www.sqlite.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3.svg)](https://getbootstrap.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Academic Project: Web Development Design (WDF)**  
> **Course**: Professional Diploma in Full Stack Web Development (SCTP) / HDSE  
> **Author / Intern**: Zaw Myo Tun  
> **Organization Scenario**: Developed for Infinity IT Solutions (IITS) client *Silent Library*

---

## 📖 Project Overview & Academic Brief

This project represents the complete end-to-end implementation for the **Web Development Design (WDF)** curriculum following the **Software Development Lifecycle (SDLC)**. 

Silent Library needed an automated, accessible web application to modernize its traditional book checkout and patron management systems. As a Full-Stack Developer intern at Infinity IT Solutions (IITS), the solution was architected using **Django** and **Bootstrap 5** to handle authentication, inventory, loan circulation, waitlists, and community reviews.

---

## 🎯 System Requirements & Modules Implemented

### 1. User Authentication & Profile Management
- Role-Based Access Control (**RBAC**) differentiating regular Library Members from Administrators / Librarians.
- Profile management with custom profile photo uploads, personal details editing, and input validation.

### 2. Search & Catalog Browsing
- Comprehensive catalog search enabling members to query books by **Title**, **Author**, **Genre/Category**, and **ISBN**.
- Book detail view displaying real-time availability status, summary, publisher details, and cover images.

### 3. Circulation, Loans & Automated Return Workflow
- One-click checkout workflow calculating loan due dates.
- Automated return logging and overdue tracking.

### 4. Smart Waitlist Queue
- Queue mechanism allowing patrons to join a waitlist when all copies of a desired title are currently loaned out.

### 5. Community Ratings & Reviews
- Feedback and rating system allowing verified readers to publish reviews and rate books from 1 to 5 stars.

### 6. Email Notification System
- Configured via Django's email backend to send automated email confirmations for book loans, due date reminders, and reservation notifications.

---

## 🛠️ Project Structure

```
silentLibrary/
├── mylms/
│   ├── library/          # Core LMS application (models, views, forms, templates)
│   │   ├── models.py     # Schema for UserProfile, Book, Loan, Waitlist, Review
│   │   ├── views.py      # Business logic & circulation workflows
│   │   ├── forms.py      # Secure form validation
│   │   └── urls.py       # Modular routing
│   ├── mylms/            # Django root configuration and settings
│   ├── static/           # Styling, scripts & UI assets
│   ├── manage.py
│   └── .env.example      # Secure environment variables template
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Local Setup Instructions
```bash
# 1. Clone repository
git clone https://github.com/Z-Dev-Coder/silentlibrary.git
cd silentlibrary

# 2. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate       # Windows
# source venv/bin/activate    # Linux/macOS

# 3. Install required packages
pip install -r requirements.txt

# 4. Configure environment (optional, for email notifications)
cp mylms/.env.example mylms/.env

# 5. Apply migrations and launch development server
cd mylms
python manage.py migrate
python manage.py runserver
```

Navigate to `http://127.0.0.1:8000/` in your browser.

---

## 📄 License

This academic coursework project is distributed under the [MIT License](LICENSE).
