from pdf_scout.custom_types import Word, HeadingScore
from typing import List, Tuple, Sequence
import re
import statistics


def font_is_bold(font_name: str) -> bool:
    return re.search(r"(Bold|BoldMT|\.B)$", font_name) is not None


def font_is_semibold(font_name: str) -> bool:
    return re.search(r"Semibold$", font_name) is not None


def font_is_bolditalic(font_name: str) -> bool:
    return re.search(r"(BoldItalic|BoldItalicMT)$", font_name) is not None


def font_is_italic(font_name: str) -> bool:
    return re.search(r"(It|Italic|ItalicMT|Oblique)$", font_name) is not None


def score_font_name(font_name: str) -> int:
    if font_is_bold(font_name):
        return 20
    elif font_is_semibold(font_name):
        return 15
    elif font_is_bolditalic(font_name):
        return 10
    elif font_is_italic(font_name):
        return 5
    return 0


def score_font_size(font_size: float) -> float:
    # TODO: make more sophisticated; steps should be exponential
    return font_size


def score_word_length(length: int) -> float:
    MIN_THRESHOLD = 4  # penalise if < this length
    MAX_THRESHOLD = 150  # don't penalise if <= this length
    STARTING_SCORE = 170
    if MIN_THRESHOLD <= length <= MAX_THRESHOLD:
        return STARTING_SCORE
    elif length > MAX_THRESHOLD:
        return STARTING_SCORE - (length if length <= STARTING_SCORE else STARTING_SCORE)
    else: # length < MIN_THRESHOLD:
        return STARTING_SCORE * length / MIN_THRESHOLD


def calculate_font_score(font_name: str, font_size: float):
    font_name_score = score_font_name(font_name)
    font_size_score = score_font_size(font_size)
    return font_name_score, font_size_score, font_name_score + font_size_score

def score_capitalisation(first_word: Word):
    match = re.search(r"[0-9aA-zZ]", first_word["text"][0])
    if match:
        return 0 if re.match(r"[a-z]", match.group(0)) is None else 10
    return 0

def get_font_score_for_word(word: Word) -> float:
    font_name = word["fontname"]
    font_size: float = word["size"]
    _, __, font_score = calculate_font_score(font_name, font_size)
    return round(font_score, 2)


def get_heading_score(paragraph: List[List[Word]]) -> HeadingScore:
    font_name_score: int = min([
        score_font_name(word["fontname"]) for line in paragraph for word in line
    ])
    font_size_score: float = min([
        score_font_size(word["size"]) for line in paragraph for word in line
    ])
    length: int = len(" ".join([word["text"] for line in paragraph for word in line]).strip(" []()./|"))

    font_score = font_name_score + font_size_score
    word_length_score = score_word_length(length)

    capitalisation_score = score_capitalisation(paragraph[0][0])
    score = round(font_name_score + font_size_score + word_length_score + capitalisation_score, 2)

    return {
        "font_name": round(font_name_score, 2),
        "font_size": round(font_size_score, 2),
        "word_length": round(word_length_score, 2),
        "capitalisation": round(capitalisation_score, 2),
        "font": round(font_score, 2),
        "overall": score,
    }


def guess_body_score(word_list: Sequence[Tuple[HeadingScore, Word]]) -> float:
    return statistics.mode([score["font"] for score, _ in word_list])


def score_paragraphs(
    all_lines: List[List[Word]],
    heading_paragraphs: List[List[List[Word]]]
) -> List[Tuple[HeadingScore, List[List[Word]]]]:
    all_words_scores: List[float] = [
        get_font_score_for_word(word) for line in all_lines for word in line
    ]
    body_font_score: float = statistics.mode([score for score in all_words_scores])

    scored_heading_paragraphs = [
        (get_heading_score(paragraph), paragraph) for paragraph in heading_paragraphs
    ]

    # ignore all body text
    scored_heading_paragraphs = [
        (score, paragraph)
        for score, paragraph in scored_heading_paragraphs
        if score["font"] > body_font_score
    ]

    return scored_heading_paragraphs
