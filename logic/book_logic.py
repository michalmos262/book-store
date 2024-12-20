from dto.book_dto import BookDTO
from dto.book_filter_parameters_dto import BookFilterParametersDTO
from enums.persistence_method import PersistenceMethod
from repository.postgres_book_repository import PostgresBookRepository


class BookLogic:
    def __init__(self):
        self.postgres_book_repository = PostgresBookRepository()
        self.books_counter = self.postgres_book_repository.get_books_total()

    def create_book(self, book_dto: BookDTO):
        book: BookDTO = self.postgres_book_repository.create_book(
            BookDTO(
                id=self.books_counter+1,
                title=book_dto.title,
                author=book_dto.author,
                year=book_dto.year,
                price=book_dto.price,
                genres=book_dto.genres))

        self.books_counter += 1
        return book

    def get_book_by_id(self, id, persistence_method: PersistenceMethod):
        if persistence_method == PersistenceMethod.POSTGRES:
            return self.postgres_book_repository.get_book_by_id(id)
        elif persistence_method == PersistenceMethod.MONGO:
            return NotImplemented

    def get_book_by_title(self, title, persistence_method: PersistenceMethod):
        if persistence_method == PersistenceMethod.POSTGRES:
            return self.postgres_book_repository.get_book_by_title(title)
        elif persistence_method == PersistenceMethod.MONGO:
            return NotImplemented

    def get_books_total(self, persistence_method: PersistenceMethod):
        if persistence_method == PersistenceMethod.POSTGRES:
            return self.postgres_book_repository.get_books_total()
        elif persistence_method == PersistenceMethod.MONGO:
            return NotImplemented

    def delete_book_by_id(self, id):
        return self.postgres_book_repository.delete_book_by_id(id)

    def get_filtered_books(self, filter_parameters: BookFilterParametersDTO, persistence_method: PersistenceMethod):
        return NotImplemented