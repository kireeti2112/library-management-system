# **Library Management System**
A library management system to streamline book and member management. This system allows librarians to import books from an external API (Frappe API), handle book records, and track book quantities.

# Features
Book Import: Import books from the Frappe API with filters for title, author, ISBN, publisher, and a specified quantity.
Book Management: Add, delete, and update book information.
Member Management: Directly managed by the librarian without a login system.
Flash Messages: User feedback provided for actions, including warnings for duplicate entries.


# Technologies
Backend: Python, SQLAlchemy, Flask
Frontend: HTML, Jinja
Database: MySQL
External API: Frappe API

# Installation
*Clone the Repository:*
git clone https://github.com/your-username/library-management-system.git
cd library-management-system

*Create a Virtual Environment:*
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`


*Install Dependencies:*
pip install -r requirements.txt
``
