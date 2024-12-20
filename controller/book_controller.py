from flask import request

from dto.genres_dto import Genres
from main import app
from logic.book_logic import BookLogic

RESULT_KEY = "result"
ERROR_MESSAGE_KEY = "errorMessage"


def get_book_not_found_error(book_id: int):
    error_msg = f"Error: no such Book with id {book_id}"
    return {ERROR_MESSAGE_KEY: error_msg}, 404


class BookController:
    def __init__(self):
        self.book_logic = BookLogic()

    @app.route("/books/health", methods=["GET"])
    def get_health(self):
        return "OK", 200

    @app.route("/book", methods=["POST"])
    def create_book(self):
        response = {}
        status = 200

        title = request.json["title"]
        author = request.json["author"]
        year = request.json["year"]
        price = request.json["price"]
        genres = request.json["genres"]

        existing_book = self.book_logic.get_book_by_title(title.lower())
        if existing_book is not None:
            error_msg = f"Error: Book with the title {title} already exists in the system"
            response[ERROR_MESSAGE_KEY] = error_msg
            status = 409

        else:
            start_year = 1940
            end_year = 2100
            if int(year) < start_year or int(year) > end_year:
                error_msg = f"Error: Can't create new Book that its year {year} is not in the accepted range [{start_year} -> {end_year}]"
                response[ERROR_MESSAGE_KEY] = error_msg
                status = 409
            elif int(price) < 0:
                error_msg = f"Error: Can't create new Book with negative price"
                response[ERROR_MESSAGE_KEY] = error_msg
                status = 409
            else:
                book = self.book_logic.create_book(title, author, year, price, genres)
                response[RESULT_KEY] = book.id

        return response, status

    @app.route("/books/total", methods=["GET"])
    def get_books_total(self):
        total_books = self.book_logic.get_books_total()
        response = {RESULT_KEY: total_books}

        return response, 200

    @app.route("/books", methods=["GET"])
    def get_books(self):
        author = request.args.get('author')
        price_bigger_than = request.args.get('price-bigger-than')
        price_less_than = request.args.get('price-less-than')
        year_bigger_than = request.args.get('year-bigger-than')
        year_less_than = request.args.get('year-less-than')
        genres = request.args.get('genres')

        filtered_books = []
        response = {}

        if genres is not None:
            genres = set(genres.split(','))
        existing_books = self.book_logic.get_filtered_books(author,
                                                            price_bigger_than,
                                                            price_less_than,
                                                            year_bigger_than,
                                                            year_less_than,
                                                            genres)

        for book in existing_books:
            if genres is not None:
                possible_genres = {genre.value for genre in Genres}
                if not genres.issubset(set(possible_genres)):
                    return 400
                if not genres & set(book.genres):
                    continue
            filtered_books.append(book)

        filtered_books.sort(key=lambda book: book.title.lower())

        response[RESULT_KEY] = []
        for filtered_book in filtered_books:
            response[RESULT_KEY].append(filtered_book.__dict__)

        return response, 200

    @app.route("/book", methods=["GET"])
    def get_book(self):
        book_id = int(request.args.get('id'))
        status = 200
        existing_book = self.book_logic.get_book_by_id(book_id)

        if existing_book.id == book_id:
            response = {RESULT_KEY: existing_book.__dict__}
        else:
            response, status = {}, get_book_not_found_error(book_id)

        return response, status

    @app.route("/book", methods=["PUT"])
    def update_book_price(self):
        book_id = int(request.args.get('id'))
        new_price = int(request.args.get('price'))
        response = {}
        status = 200
        existing_book = self.book_logic.get_book_by_id(book_id)

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

    @app.route("/book", methods=["DELETE"])
    def delete_book(self):
        book_id = int(request.args.get('id'))
        response = {}
        status = 200
        existing_book = self.book_logic.get_book_by_id(book_id)

        if existing_book is not None:
            self.book_logic.delete_book_by_id(book_id)
            total_books = self.book_logic.get_books_total()
            response[RESULT_KEY] = total_books
        else:
            response, status = get_book_not_found_error(book_id)

        return response, status
