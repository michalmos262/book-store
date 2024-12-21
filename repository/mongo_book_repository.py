import mongoengine as me
from typing import List
from dto.book_dto import BookDTO
from dto.book_filter_parameters_dto import BookFilterParametersDTO
from repository.abstract_book_repository import AbstractBookRepository

# Database configuration
HOSTNAME = "localhost"
PORT = "27017"
DB_NAME = "books"
DB_TABLE_NAME = "books"

# Connect to MongoDB with mongoengine
me.connect(DB_NAME, host=f"mongodb://{HOSTNAME}:{PORT}/{DB_NAME}")


# Mongoengine Book model
class Book(me.Document):
    meta = {'collection': DB_TABLE_NAME}

    rawid = me.IntField(primary_key=True)
    title = me.StringField(required=True)
    author = me.StringField(required=True)
    year = me.IntField(required=True)
    price = me.IntField(required=True)
    genres = me.ListField(me.StringField(), required=True)

    # Ensure genres are always in uppercase when saving
    def save(self, *args, **kwargs):
        # Convert genres to uppercase before saving
        self.genres = [genre.upper() for genre in self.genres]
        super().save(*args, **kwargs)


# Convert genres list to a proper list of uppercase strings
def convert_genres_list_to_str(genres: List[str]) -> List[str]:
    return [genre.upper() for genre in genres]


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
        genres=book.genres  # No need to use ast.literal_eval anymore
    )


class MongoBookRepository(AbstractBookRepository):
    def create_book(self, book_dto: BookDTO) -> BookDTO:
        # Insert data into MongoDB
        new_book = Book(
            rawid=book_dto.id,
            title=book_dto.title,
            author=book_dto.author,
            year=book_dto.year,
            price=book_dto.price,
            genres=convert_genres_list_to_str(book_dto.genres)
        )
        new_book.save()
        return get_book_dto(new_book)

    def get_books_total(self) -> int:
        return Book.objects.count()

    def get_book_by_title(self, title: str) -> BookDTO | None:
        book = Book.objects(title__icontains=title).first()
        return get_book_dto(book)

    def get_book_by_id(self, id: int) -> BookDTO | None:
        book = Book.objects(rawid=id).first()  # Use rawid for querying by primary key
        return get_book_dto(book)

    def delete_book_by_id(self, id: int) -> bool:
        result = Book.objects(rawid=id).delete()
        return result > 0

    def get_books(self, book_filter_parameters: BookFilterParametersDTO) -> List[BookDTO]:
        query = {}

        # Add filters dynamically
        if book_filter_parameters.author:
            query["author__icontains"] = book_filter_parameters.author

        if book_filter_parameters.price_bigger_than is not None:
            query["price__gt"] = book_filter_parameters.price_bigger_than

        if book_filter_parameters.price_less_than is not None:
            query["price__lt"] = book_filter_parameters.price_less_than

        if book_filter_parameters.year_bigger_than is not None:
            query["year__gt"] = book_filter_parameters.year_bigger_than

        if book_filter_parameters.year_less_than is not None:
            query["year__lt"] = book_filter_parameters.year_less_than

        if book_filter_parameters.genres:
            query["genres__in"] = [genre.upper() for genre in
                                   book_filter_parameters.genres]  # Ensure genres are uppercase

        # Execute the query and fetch results
        filtered_books = Book.objects(**query)

        # Map to DTOs
        filtered_books_dto = [get_book_dto(book) for book in filtered_books]

        return filtered_books_dto
