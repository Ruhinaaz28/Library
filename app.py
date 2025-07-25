from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# ---------------- DATABASE INIT ----------------

def init_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Admin', 'Librarian', 'Member'))
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE,
            quantity INTEGER NOT NULL DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            return_date TEXT,
            actual_return_date TEXT,
            fine REAL DEFAULT 0,
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn



# ---------------- AUTH ROUTES ----------------


@app.route('/')
def home():
    return redirect(url_for('login'))

'''@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = get_user_role(username, password)

        if role:
            session['username'] = username
            session['role'] = role
            if role == 'Admin':
                return redirect('/admin/dashboard')
            elif role == 'Librarian':
                return redirect('/librarian/dashboard')
            else:
                return redirect('/member/dashboard')
        else:
            error = 'Invalid credentials'
    return render_template('login.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = get_user_role(username, password)  # Replace with your actual user validation logic

        if role:
            session['username'] = username
            session['role'] = role
            if role == 'Admin':
                return redirect('/admin/dashboard')
            elif role == 'Librarian':
                return redirect('/librarian/dashboard')
            else:
                return redirect('/member/dashboard')
        else:
            error = 'Invalid credentials'
    return render_template('login.html', error=error)'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = get_user_role(username, password)

        if role:
            session['username'] = username
            session['role'] = role
            if role == 'Admin':
                return redirect('/admin/dashboard')
            elif role == 'Librarian':
                return redirect('/librarian/dashboard')
            else:
                return redirect('/member/dashboard')
        else:
            error = 'Invalid credentials'
    return render_template('login.html', error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            return redirect('/')
        except sqlite3.IntegrityError:
            return render_template('signup.html', error="Username already exists")
        finally:
            conn.close()
    return render_template('signup.html')


def get_user_role(username, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    return render_template('dashboard.html', username=session['username'], role=session['role'])


# ---------------- BOOK MANAGEMENT ----------------

@app.route('/books')
def books():
    if 'username' not in session:
        return redirect('/')
    conn = sqlite3.connect('library.db')
    books = conn.execute("SELECT * FROM books").fetchall()
    conn.close()
    return render_template('books.html', books=books)


# Add Book (GET to show form, POST to submit)
'''@app.route('/admin/books/add', methods=['GET', 'POST'])
def add_book():
    if 'username' not in session or session['role'] != 'admin':
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        quantity = request.form['quantity']

        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute("INSERT INTO books (title, author, quantity) VALUES (?, ?, ?)", (title, author, quantity))
        conn.commit()
        conn.close()

        flash("Book added successfully!")
        return redirect('/admin/books')

    return render_template('add_book.html')'''

@app.route('/admin/books/add', methods=['GET', 'POST'])
def add_book():
    if 'username' not in session or session['role'] != 'admin':
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        quantity = request.form['quantity']

        # Correct DB operation using with block
        with sqlite3.connect('library.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO books (title, author, quantity) VALUES (?, ?, ?)", 
                      (title, author, quantity))
            conn.commit()

        flash("Book added successfully!")
        return redirect('/admin/books')

    return render_template('add_book.html')


@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    if session.get('role') != 'Admin':
        return redirect('/dashboard')
    conn = sqlite3.connect('library.db')
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return redirect('/books')

@app.route('/admin/users/add', methods=['GET', 'POST'])
def add_user():
    if 'username' not in session or session['role'] != 'admin':
        return redirect('/login')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        try:
            with sqlite3.connect('library.db', timeout=10) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                          (username, password, role))
                conn.commit()
            flash("User added successfully!")
            return redirect('/admin/users')
        except sqlite3.OperationalError as e:
            flash("Database is locked. Please try again later.")
            return redirect('/admin/users')

    return render_template('add_user.html')



@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/librarian/dashboard')
def librarian_dashboard():
    return render_template('librarian_dashboard.html')

@app.route('/member/dashboard')
def member_dashboard():
    return render_template('member_dashboard.html')


# ---------------- MEMBER MANAGEMENT ----------------

@app.route('/members')
def members():
    if session.get('role') != 'Admin':
        return redirect('/dashboard')
    conn = sqlite3.connect('library.db')
    members = conn.execute("SELECT * FROM members").fetchall()
    conn.close()
    return render_template('members.html', members=members)


@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if session.get('role') != 'Admin':
        return redirect('/dashboard')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        conn = sqlite3.connect('library.db')
        conn.execute("INSERT INTO members (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
        conn.commit()
        conn.close()
        return redirect('/members')
    return render_template('add_member.html')


# ---------------- ISSUE / RETURN ----------------

@app.route('/issue_return', methods=['GET', 'POST'])
def issue_return():
    if session.get('role') not in ['Admin', 'Librarian']:
        return redirect('/dashboard')
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        user_id = request.form['user_id']
        book_id = request.form['book_id']
        issue_date = datetime.now().strftime('%Y-%m-%d')
        return_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        cursor.execute("INSERT INTO transactions (user_id, book_id, issue_date, return_date) VALUES (?, ?, ?, ?)",
                       (user_id, book_id, issue_date, return_date))
        cursor.execute("UPDATE books SET quantity = quantity - 1 WHERE id = ?", (book_id,))
        conn.commit()

    books = cursor.execute("SELECT * FROM books").fetchall()
    users = cursor.execute("SELECT * FROM users WHERE role = 'Member'").fetchall()
    transactions = cursor.execute(
        "SELECT t.id, u.username, b.title, t.issue_date, t.return_date, t.actual_return_date, t.fine FROM transactions t JOIN users u ON t.user_id = u.id JOIN books b ON t.book_id = b.id").fetchall()

    conn.close()
    return render_template('issue_return.html', books=books, users=users, transactions=transactions)


@app.route('/return_book/<int:transaction_id>')
def return_book(transaction_id):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    actual_return_date = datetime.now()
    cursor.execute("SELECT return_date, book_id FROM transactions WHERE id = ?", (transaction_id,))
    data = cursor.fetchone()
    return_date = datetime.strptime(data[0], '%Y-%m-%d')
    book_id = data[1]

    # Calculate fine
    fine = 0
    if actual_return_date > return_date:
        days_late = (actual_return_date - return_date).days
        fine = days_late * 2  # ₹2 fine per day

    cursor.execute("UPDATE transactions SET actual_return_date=?, fine=? WHERE id=?",
                   (actual_return_date.strftime('%Y-%m-%d'), fine, transaction_id))
    cursor.execute("UPDATE books SET quantity = quantity + 1 WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    return redirect('/issue_return')


@app.route('/admin/books')
def manage_books():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = [dict(id=row[0], title=row[1], author=row[2], quantity=row[3]) for row in cursor.fetchall()]
    conn.close()
    return render_template("manage_books.html", books=books)


# ================= USER MANAGEMENT =================
@app.route('/admin/users')
def manage_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = [dict(id=row[0], username=row[1], role=row[3]) for row in cursor.fetchall()]
    conn.close()
    return render_template("manage_users.html", users=users)


# ================= TRANSACTION TRACKING =================
@app.route('/admin/transactions')
def track_transactions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, u.username AS member, b.title AS book, t.issued_date, t.returned_date
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        JOIN books b ON t.book_id = b.id
    """)
    transactions = [
        dict(id=row[0], member=row[1], book=row[2], issued_date=row[3], returned_date=row[4])
        for row in cursor.fetchall()
    ]
    conn.close()
    return render_template("track_transactions.html", transactions=transactions)



# ---------------- MAIN ----------------

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
