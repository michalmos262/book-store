from dto.book_dto import BookDTO
from dto.book_filter_parameters_dto import BookFilterParametersDTO
from enums.persistence_method import PersistenceMethod
from repository.mongo_book_repository import MongoBookRepository
from repository.postgres_book_repository import PostgresBookRepository


class BookLogic:
    def __init__(self):
        self.postgres_book_repository = PostgresBookRepository()
        self.mongo_book_repository = MongoBookRepository()
        self.books_counter = self.postgres_book_repository.get_books_total()

    def create_book(self, book_dto: BookDTO):
        book_creation_dto = BookDTO(
                id=self.books_counter+1,
                title=book_dto.title,
                author=book_dto.author,
                year=book_dto.year,
                price=book_dto.price,
                genres=book_dto.genres)

        postgres_book: BookDTO = self.postgres_book_repository.create_book(book_creation_dto)
        self.mongo_book_repository.create_book(book_creation_dto)

        self.books_counter += 1
        return postgres_book

    def update_book_price(self, book_id: int, price: int):
        self.postgres_book_repository.update_book_price(book_id, price)
        self.mongo_book_repository.update_book_price(book_id, price)

    def get_book_by_id(self, id, persistence_method: PersistenceMethod):
        if persistence_method == PersistenceMethod.POSTGRES:
            return self.postgres_book_repository.get_book_by_id(id)
        elif persistence_method == PersistenceMethod.MONGO:
            return self.mongo_book_repository.get_book_by_id(id)

    def get_book_by_title(self, title, persistence_method: PersistenceMethod):
        if persistence_method == PersistenceMethod.POSTGRES:
            return self.postgres_book_repository.get_book_by_title(title)
        elif persistence_method == PersistenceMethod.MONGO:
            return self.mongo_book_repository.get_book_by_title(title)

    def get_books_total(self, persistence_method: PersistenceMethod):
        if persistence_method == PersistenceMethod.POSTGRES:
            return self.postgres_book_repository.get_books_total()
        elif persistence_method == PersistenceMethod.MONGO:
            return self.mongo_book_repository.get_books_total()

    def delete_book_by_id(self, id):
        self.mongo_book_repository.delete_book_by_id(id)
        return self.postgres_book_repository.delete_book_by_id(id)

    def get_filtered_books(self, book_filter_parameters: BookFilterParametersDTO,
                           persistence_method: PersistenceMethod):
        if persistence_method == PersistenceMethod.POSTGRES:
            return self.postgres_book_repository.get_books(book_filter_parameters)
        elif persistence_method == PersistenceMethod.MONGO:
            return self.mongo_book_repository.get_books(book_filter_parameters)
