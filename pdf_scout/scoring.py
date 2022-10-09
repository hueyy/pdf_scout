from numbers import Number
from pdf_scout.logger import debug_log
from pdf_scout.types import Word, HeadingScore
from typing import List, Tuple
import re
import statistics


def score_font_name(font_name: str) -> Number:
    if re.search(r"(Bold|BoldMT)$", font_name):
        return 20
    elif re.search(r"Semibold$", font_name):
        return 15
    elif re.search(r"(BoldItalic|BoldItalicMT)$", font_name):
        return 10
    elif re.search(r"(It|Italic|ItalicMT|Oblique)$", font_name):
        return 5
    return 0


def score_font_size(font_size: Number) -> Number:
    # TODO: make more sophisticated; steps should be exponential
    return font_size


def score_word_length(length: int) -> Number:
    MIN_THRESHOLD = 4  # penalise if < this length
    MAX_THRESHOLD = 80  # don't penalise if <= this length
    STARTING_SCORE = 100
    if MIN_THRESHOLD <= length <= MAX_THRESHOLD:
        return STARTING_SCORE
    elif length > MAX_THRESHOLD:
        return STARTING_SCORE - (length if length <= STARTING_SCORE else STARTING_SCORE)
    elif length < MIN_THRESHOLD:
        return STARTING_SCORE * length / MIN_THRESHOLD


def get_heading_score(word: Word) -> HeadingScore:
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


def guess_body_score(word_list: Tuple[HeadingScore, Word]) -> Number:
    return statistics.mode([score["font"] for score, _ in word_list])


def score_words(
    all_words: List[Word], non_body_words: List[Word]
) -> List[Tuple[HeadingScore, Word]]:
    scored_all_words: List[Tuple[HeadingScore, Word]] = [
        (get_heading_score(word), word) for word in all_words
    ]
    body_score = guess_body_score(scored_all_words)

    scored_non_body_words = [(get_heading_score(word), word) for word in non_body_words]
    # ignore all body text
    scored_non_body_words = [
        (score, word)
        for score, word in scored_non_body_words
        if score["font"] > body_score
    ]

    debug_log("score_words locals:", body_score, scored_non_body_words)

    return scored_non_body_words
