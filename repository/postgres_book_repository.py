import ast

from dto.book_dto import BookDTO
from repository.abstract_book_repository import AbstractBookRepository
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
USERNAME = "postgres"
PASSWORD = "docker"
HOSTNAME = "localhost"
PORT = "5432"
DB_NAME = "books"
DB_TABLE_NAME = "books"

# Create the database engine
DATABASE_URL = f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DB_NAME}"
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
    genres = Column(String, nullable=False)


# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()


def convert_genres_list_to_str(self, genres: list) -> str:
    return f'["{",".join(map(str, genres))}"]'


class PostgresBookRepository(AbstractBookRepository):
    def create_book(self, book_dto: BookDTO) -> BookDTO:
        # Insert data into the Books table
        new_book = Book(
            rawid=book_dto.id,
            title=book_dto.title,
            author=book_dto.author,
            year=book_dto.year,
            price=book_dto.price,
            genres=convert_genres_list_to_str(book_dto.genres)
        )
        session.add(new_book)
        session.commit()

        # Convert the string to a list
        genres_list = ast.literal_eval(new_book.genres)

        return BookDTO(id=new_book.rawid,
                       title=new_book.title,
                       author=new_book.author,
                       year=new_book.year,
                       price=new_book.price,
                       genres=genres_list)

    def get_books_total(self) -> int:
        return session.query(Book).count()

    def get_book_dto(self, book: Book) -> BookDTO | None:
        if book is None:
            return None

        return BookDTO(id=book.rawid,
                       title=book.title,
                       author=book.author,
                       year=book.year,
                       price=book.price,
                       genres=book)

    def get_book_by_title(self, title: str) -> BookDTO | None:
        book: Book | None = session.query(Book).filter(Book.title.ilike(title)).first()
        return self.get_book_dto(book)

    def get_book_by_id(self, id: int) -> BookDTO | None:
        book: Book | None = session.query(Book).filter(Book.rawid == id).first()
        return self.get_book_dto(book)

    def delete_book_by_id(self, id: int) -> None:
        existing_book = session.query(Book).filter(Book.rawid == id).first()
        if existing_book:
            session.delete(existing_book)
            session.commit()
