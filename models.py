from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String(200), nullable = False)
    author = db.Column(db.String(20),nullable = False)
    isbn = db.Column(db.String(13),unique = True, nullable = False)
    stock = db.Column(db.Integer, nullable = False)
    publisher = db.Column(db.String(200))
    num_pages = db.Column(db.Integer)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(100), nullable = False)
    debt = db.Column(db.Float , nullable = False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable = False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable = False)
    issue_date = db.Column(db.DateTime, nullable = False)
    return_date = db.Column(db.DateTime)
    rent_fee = db.Column(db.Float) 
