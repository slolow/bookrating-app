"""
import csv to databank
"""

import os
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Create books table
db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER NOT NULL)")

# import books from csv to books table from database
books = pd.read_csv('books.csv', sep=',')

for index, row in books.iterrows():
    #print(row['year'])
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {'isbn': row['isbn'], 'title': row['title'], 'author': row['author'], 'year': int(row['year'])})

db.commit()
