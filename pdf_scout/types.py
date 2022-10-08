from numbers import Number

from typing import TypedDict


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
