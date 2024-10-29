import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify,flash
from sqlalchemy import or_
from models import db, Book, Member, Transaction
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SECRET_KEY'] = 'lbs'
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/books', methods = ['GET', 'POST'])
def books():
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        book = Book.query.get(book_id)
        if book:
            db.session.delete(book)
            db.session.commit()
            return redirect(url_for('books'))
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

@app.route('/import_books', methods = ['GET','POST'])
def import_books():
    if request.method == "POST":
        num_books = int(request.form.get('num_books', 10))  # Default to 10 if not provided
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        publisher = request.form.get('publisher')
        
        # Base URL of the Frappe library API
        url = "https://www.frappe.io/api/method/frappe-library"
        
        params = {
            "title": title,
            "authors": author,
            "isbn": isbn,
            "publisher": publisher,
            "page": 1  # Starting page
        }
        
        books_fetched = []
        
        try:
            while len(books_fetched) < num_books:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json().get('message', [])
                    books_fetched.extend(data)
                    
                    # Stop if no more books are available
                    if not data:
                        break

                    # Go to the next page if we need more books
                    params["page"] += 1
                else:
                    return flash("failed to fetch data", "danger")
            
            # Trim the books to the requested amount
            books_fetched = books_fetched[:num_books]

            # Insert books into the database
            for book in books_fetched:
                existing_books = Book.query.filter_by(isbn = book.get('isbn')).all()
                if existing_books == []:
                    new_book = Book(
                        title=book.get('title'),
                        author=book.get('authors'),
                        isbn=book.get('isbn'),
                        stock = 5,
                        publisher=book.get('publisher'),
                        num_pages = book.get('  num_pages')
                    )
                    db.session.add(new_book)
            
            db.session.commit()  # Commit all new records at once
            flash(f"{len(books_fetched)} books fetched successfully", "success")
            return redirect(url_for('books'))
        
        except Exception as e:
            db.session.rollback() 
            flash(e, "danger")
            return redirect(url_for('import_books'))
        
    return render_template('import_books.html')

@app.route('/members',methods = ['GET', 'POST'])
def members():
    if request.method == "POST":
        try:
            id = request.form.get('id')
            member = Member.query.get(id)
            if id:
                db.session.delete(member)
                db.session.commit()
            else:
                flash("Member Not Found","danger")
        except:
            flash("Enter correct id","danger")
    members = Member.query.all()
    return render_template('members.html', members = members)

@app.route('/add_members',methods = ['GET', 'POST'])
def add_members():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        new_member = Member(name = name, email = email, debt = 0.00)
        try:
            db.session.add(new_member)
            db.session.commit()
            flash("Added member successfully","success")
        except:
            flash("Email already exists", "danger")
        return redirect(url_for('members'))
    return render_template('add_members.html')

@app.route('/transactions', methods = ['GET'])
def transactions():
    transactions = Transaction.query.all()
    return render_template('transactions.html', transactions = transactions)

@app.route('/issue_book', methods=['GET','POST'])
def issue_book():
    if request.method == 'POST':
        book_id = request.form['book_id']
        member_id = request.form['id']
        book = Book.query.get(book_id)
        member = Member.query.get(member_id)
        try:
            if book.stock > 0 and member.debt < 500:
                book.stock -= 1
                new_transaction = Transaction(book_id = book.book_id, member_id = member.id, issue_date = datetime.datetime.now(), rent_fee = member.debt + 100)
                db.session.add(new_transaction)
                member.debt += 100
                db.session.commit()
                flash("Issued book succesfully","success")
                return redirect(url_for('transactions'))
        except Exception as e:
            flash("Enter valid book ID", "danger")
    return render_template('issue_book.html')

@app.route('/return_book',methods = ['GET','POST'])
def return_book():
    if request.method == 'POST':
        try:
            id = request.form['id']
            transaction = Transaction.query.get(id)
            member_id = transaction.member_id
            member = Member.query.get(member_id)
            book = Book.query.get(transaction.book_id)
            transaction.return_date = datetime.datetime.now()
            if member.debt - 100 >= 0:
                member.debt -= 100
            book.stock += 1
            db.session.commit()
            flash("Returned successfully","success")
            return redirect(url_for('transactions'))
        except Exception as e:
            flash(e,"danger")
    transactions = Transaction.query.filter_by(return_date = None).all()
    return render_template('return_book.html', transactions = transactions)



@app.route('/search', methods = ['POST','GET'])
def search():
    if request.method == "POST":
        query = request.form['query']
        results = Book.query.filter(
        or_(
            Book.title.ilike(f"%{query}%"),
            Book.author.ilike(f"%{query}%")
        )
        ).all()
        flash("Fetched books successfully","success")
        return render_template('search.html', results= results)
    return render_template('search.html')




if __name__ == '__main__':
    app.run(debug=True)