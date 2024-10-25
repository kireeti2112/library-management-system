import datetime
from flask import Flask, render_template, request, redirect, url_for
from models import db, Book, Member, Transaction
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/books', methods = ['GET', 'POST'])
def books():
    books = Book.query.all()
    return render_template('books.html', books = books)

@app.route('/add_book', methods = ['GET','POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        stock = request.form['stock']
        publisher = request.form['publisher']
        num_pages = request.form['num_pages']
        new_book = Book(title = title, author = author, isbn = isbn, stock = stock, publisher = publisher, num_pages = num_pages)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('add_book'))
    return render_template('add_book.html')

@app.route('/members',methods = ['GET', 'POST'])
def members():
    members = Member.query.all()
    return render_template('members.html', members = members)

@app.route('/add_members',methods = ['GET', 'POST'])
def add_members():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        new_member = Member(name = name, email = email, debt = 0.00)
        db.session.add(new_member)
        db.session.commit()
        return redirect(url_for('members'))
    return render_template('add_members.html')

@app.route('/issue_book', methods=['GET','POST'])
def issue_book():
    if request.method == 'POST':
        book_id = request.form['book_id']
        member_id = request.form['id']
        book = Book.query.get(book_id)
        member = Member.query.get(member_id)

        if book.stock > 0:
            book.stock -= 1
            new_transaction = Transaction(book_id = book.book_id, member_id = member.id, issue_date = datetime.datetime.now(), rent_fee = member.debt + 100)
            db.session.add(new_transaction)
            member.debt += 100
            db.session.commit()
            return redirect(url_for('transactions'))
    return render_template('issue_book.html')

@app.route('/return_book',methods = ['POST'])
def return_book():
    if request.form == "POST":
        id = request.form['id']
        book_id = request.form['book_id']
        book = Book.query.get['book_id']
        member = Member.query.get['id']

    return render_template('return_book.html')

@app.route('/transactions', methods = ['GET'])
def transactions():
    transactions = Transaction.query.all()
    return render_template('transactions.html', transactions = transactions)

@app.route('/search', methods = ['GET'])
def search():
    query = request.args.get('query')
    books = Book.query.filter(Book.title.contains(query) | Book.author.contains(query)).all()
    return render_template('search.html',books = books)

@app.route('/import_books', methods = ['GET','POST'])
def import_books():
    num_books = request.form.get('num_books')
    response = requests.get(f'https://frappe.io/api/method/frappe-library?page=2&title=and')
    books_data = response.json().get('message',[])
    for book_data in books_data:
        existing_books = Book.query.filter_by(isbn=book_data['isbn']).first()
        if existing_books is None:
            new_book = Book(book_id = book_data['bookID'],
                title = book_data['title'],
                author = book_data['authors'],
                isbn = book_data['isbn'],
                stock = 5,
                publisher = book_data.get('publisher', 'Unknown')
            )
            db.session.add(new_book)
    db.session.commit()
    return redirect(url_for('books'))


if __name__ == '__main__':
    app.run(debug=True)