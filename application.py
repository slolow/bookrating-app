import os
import flask
import requests
import hashlib

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
#from flask.session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def stringHash(password):
    return hashlib.sha224((password + '123').encode('utf-8')).hexdigest()


@app.route("/", methods=["GET", "POST"])
def index():
    """Login"""

    session["userName"] = None
    # Get form information
    userName = request.form.get("userName")
    password = request.form.get("password")

    # No password entered
    if password is None:
        return render_template("index.html", falseLoginData=False)
    # password entered
    else:
        # Make Sure userName exist
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": userName}).rowcount == 0:
            return render_template("index.html", falseLoginData=True)

        # Make sure password is correct
        password_databank = db.execute("SELECT passwords FROM users WHERE username = :username", {"username": userName}).fetchone()[0]
        passwordHash = stringHash(password)
        if passwordHash == password_databank:
            session["userName"] = userName
            return redirect(url_for("bookSearch"))
        else:
            return render_template("index.html", falseLoginData=True)

@app.route("/signUp", methods=["POST"])
def signUp():
    """Sign up"""

    # Get form information
    userName = request.form.get("userName")
    password = request.form.get("password")
    repeatPassword = request.form.get("repeatPassword")

    # Make Sure userName does not allready exist
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": userName}).rowcount != 0:
        return render_template("signUp.html", ErroruserNameNotAvailable=True, passwordDismatch=False)

    # Make sure both passwords are identical
    if password != repeatPassword:
        return render_template("signUp.html", ErroruserNameNotAvailable=False, passwordDismatch=True)
    # Save username and password in database
    elif password is not None:
        passwordHash = stringHash(password)
        db.execute("INSERT INTO users (username, passwords) VALUES (:username, :password)", {"username": userName, "password": passwordHash})
        db.commit()
        return render_template("successfullySignUp.html", userName=userName)
    else:
        return render_template("signUp.html", ErrorUserNameNotAvailable=False, passwordDismatch=False)


@app.route("/bookSearch")
def bookSearch():
    """book search"""
    # Make sure a user is loged in
    if session["userName"] is not None:
        return render_template("bookSearch.html", bookNotAvailable=False, userName=session["userName"])
    else:
        return redirect(url_for("index"))


@app.route("/searchResults", methods=["POST"])
def searchResults():
    """Search for books and list them"""
    # Get Book Informations that the user searchs for
    bookInfo = request.form.get("bookInfo")
    bookInfoLike = '%' + bookInfo + '%'
    bookResults = db.execute("SELECT id, author, title, year FROM books WHERE isbn LIKE :bookInfo OR title LIKE :bookInfo OR author LIKE :bookInfo", {"bookInfo": bookInfoLike}).fetchall()
    if len(bookResults) !=0:
        return render_template("bookResults.html", bookInfo=bookInfo, bookResults=bookResults, userName=session["userName"])
    else:
        return render_template("bookSearch.html", bookNotAvailable=True, userName=session["userName"])


@app.route("/book/<int:bookId>", methods=["GET", "POST"])
def book(bookId):
    """Informations about a single Book."""
    # Make sure user is loged in
    if session["userName"] is None:
        return redirect(url_for("index"))

    # Get all the informations about the book and transform it to tuple for better presantation in html
    book = db.execute("SELECT title, author, year, isbn FROM books WHERE id = :bookId", {"bookId": bookId}).fetchone()
    bookKeys = ["Title: ", "Author: ", "Year: ", "ISBN: "]
    bookTuple = ()
    for bookInfo, key in zip(book, bookKeys):
        bookTuple += (key, str(bookInfo)),

    # Initialize value
    bookAlreadyReviewed = False

    # Get the posted review
    if request.method == "POST":
        newReview = request.form.get("bookReview")
        rate = request.form.get("inlineRadioOptions")
        # Get user_id of user that is posting  review
        user_id = db.execute("SELECT id FROM users WHERE username = :username", {"username": session["userName"]}).fetchone()[0]
        # Make sure user did not already reviewed this book
        alreadyReviewed = db.execute("SELECT book_id FROM reviews WHERE user_id= :user_id", {"user_id": user_id}).fetchall()
        alreadyReviewedList = []
        for element in alreadyReviewed:
            alreadyReviewedList.append(element[0])
        if bookId not in alreadyReviewedList:
            db.execute("INSERT INTO reviews (user_id, book_id, review, rate) VALUES (:user_id, :book_id, :review, :rate)", {"user_id": user_id, "book_id": bookId, "review": newReview, "rate": rate})
            db.commit()
        else:
            bookAlreadyReviewed = True

    # Get all reviews, rate and name of users that wrote the review
    reviews = db.execute("SELECT username, review, rate FROM users JOIN reviews ON reviews.user_id = users.id WHERE book_id = :bookId", {"bookId": bookId}).fetchall()

    # Get average rating and number of ratings for book of goodreads page
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Vk0AXQNz5OUCLlw2WCiSwQ", "isbns": book[3]})
    # Make sure goodreads has statistics for the book
    if res.status_code == 200:
        numberOfRatings = res.json()['books'][0]['work_ratings_count']
        averageRating = res.json()['books'][0]['average_rating']
        goodreadsReviewData = [('Number of ratings: ', str(numberOfRatings)), ('Average Rating: ', str(averageRating))]
    else:
        goodreadsReviewData = ['no statistics']
    return render_template("book.html", book=bookTuple, reviews=reviews, userName=session["userName"], bookId=bookId, bookAlreadyReviewed=bookAlreadyReviewed, goodreadsReviewData=goodreadsReviewData)


@app.route("/api/<isbn>")
def api(isbn):
    """ return json with book informations """
    # Make sure user is loged in
    if session["userName"] is None:
        return redirect(url_for("index"))

    # Make sure book exist
    book = db.execute("SELECT title, author, year FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
            return jsonify({"error": "Invalid book isbn"}), 404

    # Get review information
    rates = db.execute("SELECT COUNT(rate), AVG(rate) FROM reviews JOIN books on reviews.book_id = books.id WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    # check if their is a rating for the book
    # Otherwise the average rating can not be calculated
    if rates[0] == 0:
        averageRating = None
    else:
        averageRating = float(rates[1])

    return jsonify({
        "title": book[0],
        "author": book[1],
        "year": book[2],
        "isbn": isbn,
        "review_count": rates[0],
        "average_score": averageRating
    })


@app.route("/yourReviews")
def yourReviews():
    # Make sure user is loged in
    if session["userName"] is None:
        return redirect(url_for("index"))

    # Get user_id of user that want to see his reviews
    user_id = db.execute("SELECT id FROM users WHERE username = :username", {"username": session["userName"]}).fetchone()[0]

    # Get all reviews, rate and book title that wrote the review
    reviews = db.execute("SELECT review, rate, title FROM books JOIN reviews ON reviews.book_id = books.id WHERE user_id = :user_id", {"user_id": user_id}).fetchall()

    return render_template("yourReviews.html", reviews=reviews, userName=session["userName"])
