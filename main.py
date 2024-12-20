from flask import Flask

app = Flask(__name__)
HOST = "0.0.0.0"
PORT = 8574

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
