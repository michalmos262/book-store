import json
from enum import Enum


class Genres(Enum):
    SCI_FI = "SCI_FI"
    NOVEL = "NOVEL"
    HISTORY = "HISTORY"
    MANGA = "MANGA"
    ROMANCE = "ROMANCE"
    PROFESSIONAL = "PROFESSIONAL"


def convert_string_to_genres_list(input_string: str):
    return [Genres[item] for item in input_string]
