from flask import Flask, request

from dto.book_dto import BookDTO
from dto.book_filter_parameters_dto import BookFilterParametersDTO
from dto.genres_dto import Genres
from enums.persistence_method import PersistenceMethod
from logic.book_logic import BookLogic

RESULT_KEY = "result"
ERROR_MESSAGE_KEY = "errorMessage"


def get_book_not_found_error(book_id: int):
    error_msg = f"Error: no such Book with id {book_id}"
    return {ERROR_MESSAGE_KEY: error_msg}, 404


def convert_persistence_method(persistence_method: str) -> PersistenceMethod | None:
    try:
        return PersistenceMethod(persistence_method)
    except ValueError:
        return None


def get_persistence_method() -> PersistenceMethod | None:
    persistence_method_str = request.args["persistenceMethod"]
    return convert_persistence_method(persistence_method_str)


class BookController:
    def __init__(self, app: Flask):
        self.app = app
        self.book_logic = BookLogic()
        self.setup_routes()  # Ensure routes are set up during initialization

    def setup_routes(self):
        @self.app.route("/books/health", methods=["GET"])
        def get_health():
            return "OK", 200

        @self.app.route("/book", methods=["POST"])
        def create_book():
            response = {}
            status = 200

            title = request.json["title"]
            author = request.json["author"]
            year = request.json["year"]
            price = request.json["price"]
            genres = request.json["genres"]

            existing_book = self.book_logic.get_book_by_title(title.lower(), PersistenceMethod.POSTGRES)
            if existing_book is not None:
                error_msg = f"Error: Book with the title {title} already exists in the system"
                response[ERROR_MESSAGE_KEY] = error_msg
                status = 409

            else:
                start_year = 1940
                end_year = 2100
                if int(year) < start_year or int(year) > end_year:
                    error_msg = (f"Error: Can't create new Book that its year {year} is not in the accepted range ["
                                 f"{start_year} -> {end_year}]")
                    response[ERROR_MESSAGE_KEY] = error_msg
                    status = 409
                elif int(price) < 0:
                    error_msg = f"Error: Can't create new Book with negative price"
                    response[ERROR_MESSAGE_KEY] = error_msg
                    status = 409
                else:
                    book_dto = BookDTO(id=None,
                                       title=title,
                                       author=author,
                                       year=int(year),
                                       price=int(price),
                                       genres=genres)
                    book = self.book_logic.create_book(book_dto)
                    response[RESULT_KEY] = book.id

            return response, status

        @self.app.route("/books/total", methods=["GET"])
        def get_books_total():
            persistence_method = get_persistence_method()
            if persistence_method:
                total_books = self.book_logic.get_books_total(persistence_method)
                response, status = {RESULT_KEY: total_books}, 200
            else:
                response, status = {ERROR_MESSAGE_KEY: "Invalid persistence method"}, 404

            return response, status

        @self.app.route("/books", methods=["GET"])
        def get_books():
            author = request.args.get('author')
            price_bigger_than = request.args.get('price-bigger-than')
            price_less_than = request.args.get('price-less-than')
            year_bigger_than = request.args.get('year-bigger-than')
            year_less_than = request.args.get('year-less-than')
            genres = request.args.get('genres')
            persistence_method = get_persistence_method()

            # if genres was inserted not properly, case-sensitive
            if genres is not None:
                genres = list(genres.split(','))
                if not all(genre in Genres for genre in genres):
                    return 400

            book_filter_params_dto = BookFilterParametersDTO(
                author=author if author else None,
                price_bigger_than=int(price_bigger_than) if price_bigger_than else None,
                price_less_than=int(price_less_than) if price_less_than else None,
                year_bigger_than=int(year_bigger_than) if year_bigger_than else None,
                year_less_than=int(year_less_than) if year_less_than else None,
                genres=genres if genres else None
            )

            filtered_books = self.book_logic.get_filtered_books(book_filter_params_dto, persistence_method)
            filtered_books.sort(key=lambda filtered_book: filtered_book.title.lower())

            response = {RESULT_KEY: []}

            for filtered_book in filtered_books:
                response[RESULT_KEY].append(filtered_book.__dict__)

            return response, 200

        @self.app.route("/book", methods=["GET"])
        def get_book():
            book_id = int(request.args.get('id'))
            status = 200
            existing_book = self.book_logic.get_book_by_id(book_id, get_persistence_method())

            if existing_book.id == book_id:
                response = {RESULT_KEY: existing_book.__dict__}
            else:
                response, status = {}, get_book_not_found_error(book_id)

            return response, status

        @self.app.route("/book", methods=["PUT"])
        def update_book_price():
            book_id = int(request.args.get('id'))
            new_price = int(request.args.get('price'))
            response = {}
            status = 200
            existing_book = self.book_logic.get_book_by_id(book_id, get_persistence_method())

            if existing_book is not None:
                if new_price < 0:
                    error_msg = f"Error: price update for book {book_id} must be a positive integer"
                    response[ERROR_MESSAGE_KEY] = error_msg
                    status = 409
                else:
                    response[RESULT_KEY] = existing_book.price
                    existing_book.price = new_price

            if len(response) == 0:
                response, status = get_book_not_found_error(book_id)

            return response, status

        @self.app.route("/book", methods=["DELETE"])
        def delete_book():
            book_id = int(request.args.get('id'))
            response = {}
            status = 200
            existing_book = self.book_logic.get_book_by_id(book_id, PersistenceMethod.POSTGRES)

            if existing_book is not None:
                self.book_logic.delete_book_by_id(book_id)
                total_books = self.book_logic.get_books_total(PersistenceMethod.POSTGRES)
                response[RESULT_KEY] = total_books
            else:
                response, status = get_book_not_found_error(book_id)

            return response, status
