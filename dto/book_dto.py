class BookDTO:
    def __init__(self, id: int, title: str, author: str, year: int, price: int, genres: list):
        self.id = id
        self.title = title
        self.author = author
        self.year = year
        self.price = price
        self.genres = genres
