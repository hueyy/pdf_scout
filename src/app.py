from numbers import Number
import pdfplumber
import re
from itertools import groupby
from operator import itemgetter
from collections import Counter

FILE_PATH = "./pdf/test.pdf"


# def group_chars_by_attr(attr: str, chars, sort=False):
#     get_attr = itemgetter(attr)
#     if sort:
#         chars.sort(key=get_attr)
#     return [[key, [char for char in val]] for key, val in groupby(chars, key=get_attr)]


# def group_chars_by_line(chars):
#     return group_chars_by_attr(attr="bottom", chars=chars, sort=True)


def guess_left_margin(words):
    return Counter(map(lambda w: w["x0"], words)).most_common(1)[0][0]


def score_font_name(font_name: str) -> Number:
    if re.match(r"-Bold$", font_name):
        return 20
    if re.match(r"-Oblique", font_name):
        return 10
    return 0


def score_font_size(font_size: Number) -> Number:
    # TODO: make more sophisticated; steps should be exponential
    return font_size


def get_heading_score(word):
    font_name: str = word["fontname"]
    font_size: Number = word["size"]

    score = score_font_name(font_name) + score_font_size(font_size)
    return score


with pdfplumber.open(FILE_PATH) as pdf_file:
    first_page = pdf_file.pages[0]
    all_words_list = [
        page.extract_words(keep_blank_chars=True, extra_attrs=["fontname", "size"])
        for page in pdf_file.pages
    ]
    all_words = [word for page in all_words_list for word in page]

    left_margin = guess_left_margin(all_words)
    # TODO: add some margin of appreciation to account for indented headers, footnotes, etc

    all_words = list(filter(lambda w: w["x0"] == left_margin, all_words))

    all_fonts = set(map(lambda w: w["fontname"], all_words))
    all_font_sizes = set(map(lambda w: w["size"], all_words))

    for word in all_words:
        print(word["text"], get_heading_score(word))
    # for word in words:
    #     print(word["text"], word["fontname"], word["size"])
