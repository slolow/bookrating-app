# Project1 of CS50’s Web Programming with Python and JavaScript

**Demonstartion video**
https://youtu.be/6rESpya70nc

**good to know:**

  - newest Version of Werkzeug didn't worked for me --> I used Werkzeug Verison 0.16.0
  - I'm using bootstrap 4.4.1 for styling
  - Rating on book page is shown in a radio item with "bad", "ok", ...
    When clicking on:
      - "bad" --> 1
      - "ok" --> 2
      - "good" --> 3
      - "very good" --> 4
      - "excellent" --> 5
     is stored in the database. The integer values are later on used to calculate the average rating on the api/<isbn>                        route
  - Logout --> click on user name button on right corner of page

**What each file contains:**

  - In application.py is the flask app
  - In import.py is the storage from the csv into the database
  - In templates\ are all html files:
    - layout.html is the layout page
    - index.html is the login page
    - signUp.html is the sign-up page
    - successfullySignUp.html is the page that shows up when a user is succesfully signed up
    - bookSearch.html is where the user can search for books
    - bookResultes.html shows all the results from the user search for a book
    - book.html is the page for a single book
    - yourReviews.html shows all the reviews a user shared
  - In static\ are all stylesheets:
    - stylesheet.scss
    - stylesheet.css

  **Install without virtual environment:**

    needed:

     - python3, pip and git installed
     - a postgresql databank (you can use one from https://id.heroku.com/login)

      run app from terminal:
        commands:
       1. git clone https://github.com/slolow/bookrating-app.git
       2. cd bookrating-app
       3. pip install -r requirements.txt
       4. python import.py (imports books from book.csv to the databank)
       5. set FLASK_APP=application.py
       6. set FLASK_ENV=development (if desired)
       7. set DATABASE_URL=*databasse_url*
       8. flask run

  **Or install in pipenv:**

    needed:

     - python3, pip, pipx, pipenv, git
     - a postgresql databank (you can use one from https://id.heroku.com/login)

      run app from terminal:
        commands:
       1. git clone https://github.com/slolow/bookrating-app.git
       2. cd bookrating-app
       3. pipenv install -r requirements.txt --> Pipfile and Pipfile.lock should be created
       4. pipenv run python import.py (imports books from book.csv to the databank)
       5. set FLASK_APP=application.py
       6. set FLASK_ENV=development (if desired)
       7. set DATABASE_URL=*databasse_url*
       8. pipenv run flask run
