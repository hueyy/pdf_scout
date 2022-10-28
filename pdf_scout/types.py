from typing import TypedDict, List


class RawWord(TypedDict):
    text: str
    x0: float
    x1: float
    top: float
    doctop: float
    bottom: float
    fontname: str
    size: float
    page_number: int


class Word(RawWord):
    top_spacing: float
    bottom_spacing: float


class Rect(TypedDict):
    height: float
    width: float
    top: float
    bottom: float


class DocumentWords(TypedDict):
    all_words: List[Word]
    heading_words: List[Word]


class HeadingScore(TypedDict):
    font_name: float
    font_size: float
    word_length: float
    font: float
    overall: float


class Bookmark(TypedDict):
    title: str
    page_number: str
    scroll_distance: float
