from numbers import Number
import re
from typing import TypedDict
from rich import print as rprint


def score_font_name(font_name: str) -> Number:
    if re.search(r"Bold$", font_name):
        return 20
    elif re.search(r"BoldItalic$", font_name):
        return 10
    if re.search(r"(Italic|Oblique)$", font_name):
        return 5
    return 0


def score_font_size(font_size: Number) -> Number:
    # TODO: make more sophisticated; steps should be exponential
    return font_size


def score_word_length(length: int) -> Number:
    MIN_THRESHOLD = 4  # penalise if <= this length
    MAX_THRESHOLD = 80  # don't penalise if <= this length
    STARTING_SCORE = 100
    if length >= MIN_THRESHOLD and length <= MAX_THRESHOLD:
        return STARTING_SCORE
    elif length > MAX_THRESHOLD:
        return STARTING_SCORE - (length if length <= STARTING_SCORE else STARTING_SCORE)
    elif length < 4:
        return STARTING_SCORE * length / MIN_THRESHOLD


class HeadingScore(TypedDict):
    font_name: Number
    font_size: Number
    word_length: Number
    font: Number
    overall: Number


def get_heading_score(word) -> HeadingScore:
    font_name: str = word["fontname"]
    font_size: Number = word["size"]
    length: int = len(word["text"].strip(" []()./|"))

    font_name_score = score_font_name(font_name)
    font_size_score = score_font_size(font_size)
    word_length_score = score_word_length(length)

    score = round(font_name_score + font_size_score + word_length_score, 2)
    return {
        "font_name": round(font_name_score, 2),
        "font_size": round(font_size_score, 2),
        "word_length": round(word_length_score, 2),
        "font": round(font_name_score + font_size_score, 2),
        "overall": score,
    }
