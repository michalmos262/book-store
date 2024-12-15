from flask import Flask, request, g as app_ctx
import time
import logging
import os

app = Flask(__name__)

HOST = "0.0.0.0"
PORT = 8574

RESULT_KEY = "result"
ERROR_MESSAGE_KEY = "errorMessage"

REQUEST_COUNTER = 0
REQUEST_LOGGER = "request-logger"
BOOKS_LOGGER = "books-logger"
REQUESTS_LOG_FILENAME = "requests.log"
BOOKS_LOG_FILENAME = "books.log"

# Create logs directory
if not os.path.exists("logs"):
    os.makedirs("logs")

request_logger = logging.getLogger(REQUEST_LOGGER)
books_logger = logging.getLogger(BOOKS_LOGGER)

logs_format = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', datefmt='%d-%m-%Y %H:%M:%S')

# add console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logs_format)
request_logger.addHandler(console_handler)
books_logger.addHandler(console_handler)

# add file handlers
request_handler = logging.FileHandler(filename=f'logs{os.path.sep}{REQUESTS_LOG_FILENAME}')
request_handler.setFormatter(logs_format)
request_logger.addHandler(request_handler)

books_handler = logging.FileHandler(filename=f'logs{os.path.sep}{BOOKS_LOG_FILENAME}')
books_handler.setFormatter(logs_format)
books_logger.addHandler(books_handler)

# set default log level
request_logger.setLevel(logging.INFO)
books_logger.setLevel(logging.INFO)


def get_log_msg(msg):
    return f'{msg} | request #{REQUEST_COUNTER}'


@app.before_request
def before_logging():
    global REQUEST_COUNTER
    REQUEST_COUNTER += 1
    app_ctx.start_time = time.perf_counter()

    log_msg = f"Incoming request | #{REQUEST_COUNTER} | resource: {request.path} | HTTP Verb {request.method}"
    request_logger.info(msg=f'{log_msg} | request #{REQUEST_COUNTER}')


@app.after_request
def after_logging(response):
    global REQUEST_COUNTER

    response_time = time.perf_counter() - app_ctx.start_time
    response_time_in_ms = int(response_time * 1000)

    log_msg = f"request #{REQUEST_COUNTER} duration: {response_time_in_ms}ms"
    request_logger.debug(msg=f'{log_msg} | request #{REQUEST_COUNTER}')

    return response


class Book:
    id_counter = 0
    possible_genres = ["SCI_FI", "NOVEL", "HISTORY", "MANGA", "ROMANCE", "PROFESSIONAL"]

    def __init__(self, title, author, year, price, genres):
        Book.id_counter += 1
        self.id = Book.id_counter
        self.title = title
        self.author = author
        self.year = year
        self.price = price
        self.genres = genres


existing_books: list[Book] = []


@app.route("/books/health", methods=["GET"])
def get_health():
    return "OK", 200


@app.route("/book", methods=["POST"])
def create_book():
    response = {}
    status = 200

    title = request.json["title"]
    author = request.json["author"]
    year = request.json["year"]
    price = request.json["price"]
    genres = request.json["genres"]

    for existing_book in existing_books:
        if existing_book.title.lower() == title.lower():
            error_msg = f"Error: Book with the title {title} already exists in the system"
            books_logger.error(msg=get_log_msg(error_msg))
            response[ERROR_MESSAGE_KEY] = error_msg
            status = 409
            break

    if status == 200:
        start_year = 1940
        end_year = 2100
        if int(year) < start_year or int(year) > end_year:
            error_msg = f"Error: Can't create new Book that its year {year} is not in the accepted range [{start_year} -> {end_year}]"
            books_logger.error(msg=get_log_msg(error_msg))
            response[ERROR_MESSAGE_KEY] = error_msg
            status = 409
        elif int(price) < 0:
            error_msg = f"Error: Can't create new Book with negative price"
            books_logger.error(msg=get_log_msg(error_msg))
            response[ERROR_MESSAGE_KEY] = error_msg
            status = 409
        else:
            info_log_msg = f"Creating new Book with Title [{title}]"
            books_logger.info(msg=get_log_msg(info_log_msg))

            debug_log_msg = (f"Currently there are {len(existing_books)} Books in the system. New Book will be "
                             f"assigned with id {Book.id_counter + 1}")
            books_logger.debug(msg=get_log_msg(debug_log_msg))

            book = Book(title, author, year, price, genres)
            existing_books.append(book)
            response[RESULT_KEY] = book.id

    return response, status


@app.route("/books/total", methods=["GET"])
def get_books_total():
    get_books_response = get_books()
    result_list = get_books_response[0][RESULT_KEY]
    response = {RESULT_KEY: len(result_list)}

    return response, 200


@app.route("/books", methods=["GET"])
def get_books():
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

    for book in existing_books:
        if (author is not None) and (book.author.lower() != author.lower()):
            continue
        if (price_bigger_than is not None) and (book.price < int(price_bigger_than)):
            continue
        if (price_less_than is not None) and (book.price > int(price_less_than)):
            continue
        if (year_bigger_than is not None) and (book.year < int(year_bigger_than)):
            continue
        if (year_less_than is not None) and (book.year > int(year_less_than)):
            continue
        if genres is not None:
            if not genres.issubset(set(Book.possible_genres)):
                return 400
            if not genres & set(book.genres):
                continue
        filtered_books.append(book)

    filtered_books.sort(key=lambda book: book.title.lower())

    response[RESULT_KEY] = []
    for filtered_book in filtered_books:
        response[RESULT_KEY].append(filtered_book.__dict__)

    info_log_msg = f"Total Books found for requested filters is {len(filtered_books)}"
    books_logger.info(msg=get_log_msg(info_log_msg))

    return response, 200


@app.route("/book", methods=["GET"])
def get_book():
    book_id = int(request.args.get('id'))
    response = {}
    status = 200
    for existing_book in existing_books:
        if existing_book.id == book_id:
            response = {RESULT_KEY: existing_book.__dict__}

            debug_log_msg = f"Fetching book id {book_id} details"
            books_logger.debug(msg=get_log_msg(debug_log_msg))

            break
    if len(response) == 0:
        response, status = get_book_not_found_error(book_id)

    return response, status


def get_book_not_found_error(book_id: int):
    error_msg = f"Error: no such Book with id {book_id}"
    books_logger.error(msg=get_log_msg(error_msg))
    return {ERROR_MESSAGE_KEY: error_msg}, 404


@app.route("/book", methods=["PUT"])
def update_book_price():
    book_id = int(request.args.get('id'))
    new_price = int(request.args.get('price'))
    response = {}
    status = 200
    for existing_book in existing_books:
        if existing_book.id == book_id:
            if new_price < 0:
                error_msg = f"Error: price update for book {book_id} must be a positive integer"
                books_logger.error(msg=get_log_msg(error_msg))
                response[ERROR_MESSAGE_KEY] = error_msg
                status = 409
            else:
                info_log_msg = f"Update Book id [{book_id}] price to {new_price}"
                books_logger.info(msg=get_log_msg(info_log_msg))

                debug_log_msg = f"Book [{existing_book.title}] price change: {existing_book.price} --> {new_price}"
                books_logger.debug(msg=get_log_msg(debug_log_msg))

                response[RESULT_KEY] = existing_book.price
                existing_book.price = new_price

    if len(response) == 0:
        response, status = get_book_not_found_error(book_id)

    return response, status


@app.route("/book", methods=["DELETE"])
def delete_book():
    book_id = int(request.args.get('id'))
    response = {}
    status = 200
    for existing_book in existing_books:
        if existing_book.id == book_id:
            info_log_msg = f"Removing book [{existing_book.title}]"
            books_logger.info(msg=get_log_msg(info_log_msg))

            book_index_in_list = existing_books.index(existing_book)
            existing_books.pop(book_index_in_list)
            response[RESULT_KEY] = len(existing_books)

            debug_log_msg = f"After removing book [{existing_book.title}] id: [{book_id}] there are {len(existing_books)} books in the system"
            books_logger.debug(msg=get_log_msg(debug_log_msg))
            break
    if len(response) == 0:
        response, status = get_book_not_found_error(book_id)

    return response, status


@app.route("/logs/level", methods=["GET"])
def get_logger_level():
    logger_name = request.args.get('logger-name')

    if logger_name in [BOOKS_LOGGER, REQUEST_LOGGER]:
        tmp_logger = logging.getLogger(logger_name)
        logger_level = tmp_logger.getEffectiveLevel()
        return logging.getLevelName(logger_level), 200
    else:
        return f"Error: no logger with the name [{logger_name}] was found.", 404


@app.route("/logs/level", methods=["PUT"])
def set_logger_level():
    logger_name = request.args.get('logger-name')
    logger_level = request.args.get('logger-level')

    if (logger_name in [BOOKS_LOGGER, REQUEST_LOGGER]) and (logger_level in ['DEBUG', 'INFO', 'ERROR']):
        tmp_logger = logging.getLogger(logger_name)
        tmp_logger.setLevel(logger_level)
        return logger_level, 200
    else:
        return f"Error: resource not found.", 404


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
