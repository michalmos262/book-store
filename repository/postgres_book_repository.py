import ast
from operator import or_
from typing import List

from dto.book_dto import BookDTO
from dto.book_filter_parameters_dto import BookFilterParametersDTO
from repository.abstract_book_repository import AbstractBookRepository
from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound

# Database configuration
USERNAME = "postgres"
PASSWORD = "docker"
HOSTNAME = "postgres"
# HOSTNAME = "localhost"
PORT = "5432"
DB_NAME = "books"
DB_TABLE_NAME = "books"

# Create the database engine
DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True)

# Base class for ORM models
Base = declarative_base()


# Define the Books table
class Book(Base):
    __tablename__ = DB_TABLE_NAME

    rawid = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    genres = Column(String, nullable=False) # Was requested to be a string instead of multiple tables


# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()


def convert_genres_list_to_str(genres: list) -> str:
    return f'["{",".join(map(str, genres))}"]'


def get_book_dto(book: Book) -> BookDTO | None:
    if book is None:
        return None

    return BookDTO(id=book.rawid,
                   title=book.title,
                   author=book.author,
                   year=book.year,
                   price=book.price,
                   genres=ast.literal_eval(book.genres))


class PostgresBookRepository(AbstractBookRepository):
    def __init__(self):
        self.books_counter = session.query(Book).count()

    def create_book(self, book_dto: BookDTO) -> BookDTO:
        # Insert data into the Books table
        new_book = Book(
            rawid=self.books_counter+1,
            title=book_dto.title,
            author=book_dto.author,
            year=book_dto.year,
            price=book_dto.price,
            genres=convert_genres_list_to_str(book_dto.genres)
        )

        session.add(new_book)
        session.commit()
        self.books_counter += 1

        return get_book_dto(new_book)

    def update_book_price(self, book_id: int, new_price: int) -> None:
        try:
            book = session.query(Book).filter(Book.rawid == book_id).one()
            book.price = new_price
            session.commit()

        except NoResultFound:
            # Return None or handle it as per the requirement when the book is not found
            return None

    def get_books_total(self) -> int:
        return session.query(Book).count()

    def get_book_by_title(self, title: str) -> BookDTO | None:
        book: Book | None = session.query(Book).filter(Book.title.ilike(title)).first()
        return get_book_dto(book)

    def get_book_by_id(self, id: int) -> BookDTO | None:
        book: Book | None = session.query(Book).filter(Book.rawid == id).first()
        return get_book_dto(book)

    def delete_book_by_id(self, id: int) -> None:
        existing_book: Book | None = session.query(Book).filter(Book.rawid == id).first()
        if existing_book:
            session.delete(existing_book)
            session.commit()

    def get_books(self, book_filter_parameters: BookFilterParametersDTO) -> List[BookDTO]:
        query = session.query(Book)

        # Add filters dynamically
        if book_filter_parameters.author:
            query = query.filter(func.lower(Book.author) == book_filter_parameters.author.lower())

        if book_filter_parameters.price_bigger_than is not None:
            query = query.filter(Book.price > book_filter_parameters.price_bigger_than)

        if book_filter_parameters.price_less_than is not None:
            query = query.filter(Book.price < book_filter_parameters.price_less_than)

        if book_filter_parameters.year_bigger_than is not None:
            query = query.filter(Book.year > book_filter_parameters.year_bigger_than)

        if book_filter_parameters.year_less_than is not None:
            query = query.filter(Book.year < book_filter_parameters.year_less_than)

        if book_filter_parameters.genres:
            genre_filters = [Book.genres.contains(genre) for genre in book_filter_parameters.genres]
            if len(genre_filters) == 1:
                query = query.filter(genre_filters[0])  # Directly filter with the single condition
            else:
                query = query.filter(or_(*genre_filters))  # Use `or_` for multiple conditions

        # Execute the query and fetch results
        filtered_books: List[Book] = query.all()  # Corrected type hint

        # Map to DTOs
        filtered_books_dto = [
            get_book_dto(filtered_book) for filtered_book in filtered_books
        ]

        return filtered_books_dto
