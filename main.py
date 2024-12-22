from flask import Flask

from controller.book_controller import BookController

app = Flask(__name__)
HOST = "0.0.0.0"
PORT = 8574

if __name__ == "__main__":
    book_controller = BookController(app)
    app.run(host=HOST, port=PORT)
