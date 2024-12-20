class BookFilterParametersDTO:
    def __init__(self, author: str,
                 price_bigger_than: int,
                 price_less_than: int,
                 year_bigger_than: int,
                 year_less_than: int,
                 genres: list):

        self.author = author
        self.price_bigger_than = price_bigger_than
        self.price_less_than = price_less_than
        self.year_bigger_than = year_bigger_than
        self.year_less_than = year_less_than
        self.genres = genres
