# 📖 Silent Library — Modern Library Management System

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-092E20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3.svg?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Silent Library** is a feature-rich web-based Library Management System (LMS) built with Django. It provides end-to-end management of books, circulation loans, waitlists, member profiles, user reviews, and role-based permissions.

---

## ✨ Features

- 🔐 **Authentication & RBAC**: Custom user profiles, role-based access control (administrators, librarians, and members).
- 📚 **Catalog & Inventory Management**: Book catalog with ISBN, cover images, authors, categories, and real-time availability tracking.
- 🔄 **Circulation & Loans**: Automated loan tracking, issue and return workflows, renewal handling, and overdue calculation.
- ⏳ **Waitlist Queue**: Smart waitlist system when books are currently checked out.
- ⭐ **Reviews & Ratings**: Community feedback, book ratings, and member discussions.
- 📧 **Email Notifications**: Automated email alerts for due dates, overdue notices, and loan confirmations.

---

## 🛠️ Project Structure

```
silentLibrary/
├── mylms/
│   ├── library/          # Core LMS app (models, views, forms, templates)
│   ├── mylms/            # Project configuration & settings
│   ├── static/           # CSS, JavaScript & theme assets
│   ├── manage.py
│   └── .env.example      # Environment variables template
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

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Z-Dev-Coder/silentlibrary.git
   cd silentlibrary
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp mylms/.env.example mylms/.env
   # Edit mylms/.env with your email credentials (if using email features)
   ```

5. **Run migrations and start server**:
   ```bash
   cd mylms
   python manage.py migrate
   python manage.py runserver
   ```

6. Open your browser at `http://127.0.0.1:8000/`.

---

## 📄 License

Distributed under the [MIT License](LICENSE).
