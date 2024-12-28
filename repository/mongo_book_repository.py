import mongoengine as me
from typing import List
from dto.book_dto import BookDTO
from dto.book_filter_parameters_dto import BookFilterParametersDTO
from repository.abstract_book_repository import AbstractBookRepository

# Database configuration
HOSTNAME = "mongo"
# HOSTNAME = "localhost"
PORT = "27017"
DB_NAME = "books"
DB_TABLE_NAME = "books"

# Connect to MongoDB with mongoengine
me.connect(DB_NAME, host=f"mongodb://{HOSTNAME}:{PORT}/{DB_NAME}")


# Mongoengine Book model
class Book(me.Document):
    meta = {'collection': DB_TABLE_NAME}

    rawid = me.IntField(required=True)
    title = me.StringField(required=True)
    author = me.StringField(required=True)
    year = me.IntField(required=True)
    price = me.IntField(required=True)
    genres = me.ListField(me.StringField(), required=True)


# Convert book to DTO
def get_book_dto(book: Book) -> BookDTO | None:
    if not book:
        return None

    return BookDTO(
        id=book.rawid,
        title=book.title,
        author=book.author,
        year=book.year,
        price=book.price,
        genres=book.genres
    )


class MongoBookRepository(AbstractBookRepository):
    def __init__(self):
        self.books_counter = Book.objects.count()

    def create_book(self, book_dto: BookDTO) -> BookDTO:
        # Insert data into MongoDB
        new_book = Book(
            rawid=self.books_counter+1,
            title=book_dto.title,
            author=book_dto.author,
            year=book_dto.year,
            price=book_dto.price,
            genres=book_dto.genres
        )

        new_book.save()
        self.books_counter += 1

        return get_book_dto(new_book)

    def update_book_price(self, book_id: int, new_price: int) -> None:
        # Find the book by rawid (unique identifier)
        book = Book.objects(rawid=book_id).first()

        # If the book is found, update the price
        if book:
            book.update(set__price=new_price)
        else:
            return None

    def get_books_total(self) -> int:
        return Book.objects.count()

    def get_book_by_title(self, title: str) -> BookDTO | None:
        book = Book.objects(title__icontains=title).first()
        return get_book_dto(book)

    def get_book_by_id(self, id: int) -> BookDTO | None:
        book = Book.objects(rawid=id).first()
        return get_book_dto(book)

    def delete_book_by_id(self, id: int) -> bool:
        result = Book.objects(rawid=id).delete()
        return result > 0

    def get_books(self, book_filter_parameters: BookFilterParametersDTO) -> List[BookDTO]:
        query = {}

        # Add filters dynamically
        if book_filter_parameters.author:
            query["author__iexact"] = book_filter_parameters.author

        if book_filter_parameters.price_bigger_than is not None:
            query["price__gt"] = book_filter_parameters.price_bigger_than

        if book_filter_parameters.price_less_than is not None:
            query["price__lt"] = book_filter_parameters.price_less_than

        if book_filter_parameters.year_bigger_than is not None:
            query["year__gt"] = book_filter_parameters.year_bigger_than

        if book_filter_parameters.year_less_than is not None:
            query["year__lt"] = book_filter_parameters.year_less_than

        if book_filter_parameters.genres is not None:
            query["genres__in"] = [genre.upper() for genre in book_filter_parameters.genres]

        # Execute the query and fetch results
        filtered_without_genres_books = Book.objects(**query)

        # Map to DTOs
        filtered_books_dto = [get_book_dto(book) for book in filtered_without_genres_books]

        return filtered_books_dto
