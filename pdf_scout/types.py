from numbers import Number
from typing import TypedDict, List


class RawWord(TypedDict):
    text: str
    x0: Number
    x1: Number
    top: Number
    doctop: Number
    bottom: Number
    fontname: str
    size: Number
    page_number: int


class Word(RawWord):
    top_spacing: Number
    bottom_spacing: Number


class Rect(TypedDict):
    height: Number
    width: Number
    top: Number
    bottom: Number


class DocumentWords:
    all_words: List[Word]
    non_body_words: List[Word]


class HeadingScore(TypedDict):
    font_name: Number
    font_size: Number
    word_length: Number
    font: Number
    overall: Number


class Bookmark(TypedDict):
    title: str
    page_number: str
    scroll_distance: Number
