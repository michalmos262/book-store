from abc import ABC
from typing import List

from dto.book_dto import BookDTO
from dto.book_filter_parameters_dto import BookFilterParametersDTO


class AbstractBookRepository(ABC):
    def create_book(self, book_dto: BookDTO) -> BookDTO:
        return NotImplemented

    def get_book_by_id(self, id: int) -> BookDTO:
        return NotImplemented

    def get_book_by_title(self, title: str) -> BookDTO:
        return NotImplemented

    def get_books(self, book_filter_parameters: BookFilterParametersDTO) -> List[BookDTO]:
        return NotImplemented

    def get_books_total(self) -> int:
        return NotImplemented
