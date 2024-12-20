from dto.book_dto import BookDTO


class BookLogic:
    def create_book(self, title, author, year, price, genres):
        return BookDTO(title=title, author=author, year=year, price=price, genres=genres)

    def get_book_by_id(self, id):
        return BookDTO()

    def get_book_by_title(self, title):
        return BookDTO()

    def get_books_total(self):
        return 0

    def delete_book_by_id(self, id):
        return BookDTO()

    def get_filtered_books(self, author, price_bigger_than, price_less_than, year_bigger_than, year_less_than, genres):
        return []