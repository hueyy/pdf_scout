import pdfplumber
from typing import List, Tuple, Sequence
from pdf_scout.logger import debug_log
from pdf_scout.custom_types import Word
import statistics
from functools import wraps
from time import time
import pprint
import re


A4 = {"width": 21, "height": 29.7}
A4_COMMON_LEFT_MARGINS = [1.27, 1.9, 2.54, 3.18]
TAB_STOP_WIDTH = 1.27


def points_to_cm(points: float):
    return points / 72 * 2.54


def cm_to_points(cm: float):
    return cm * 72 / 2.54


def is_a4_page(page) -> bool:
    return (
        round(points_to_cm(page.width), 1) == A4["width"]
        and round(points_to_cm(page.height), 1) == A4["height"]
    )


def guess_left_margin_for_misc_document(
    counts: Sequence[Tuple[float, int]]
) -> List[float]:
    std_dev = statistics.pstdev([count for _, count in counts])
    mean = statistics.mean([count for _, count in counts])
    threshold_counts = [
        (left_margin, count)
        for left_margin, count in counts
        if count >= mean + std_dev * 5
    ]

    debug_log("guess_left_margin locals:", locals())

    if len(threshold_counts) == 2:
        # assume different left margin on odd and even pages
        return [left_margin for left_margin, _ in threshold_counts]
    else:
        # assume uniform left margin
        return (
            [threshold_counts[0][0]]
            if len(threshold_counts) == 1
            else [max(counts, key=lambda x: x[1])[0]]
        )


def guess_left_margin_for_a4_document(
    counts: Sequence[Tuple[float, int]]
) -> List[float]:
    left_margins = [left_margin for left_margin, _ in counts]
    std_dev = statistics.pstdev([count for _, count in counts])
    mean = statistics.mean([count for _, count in counts])
    for common_left_margin in A4_COMMON_LEFT_MARGINS:
        common_left_margin = round(cm_to_points(common_left_margin))
        if common_left_margin in left_margins:
            index = left_margins.index(common_left_margin)
            left_margin, count = counts[index]
            if count >= mean + std_dev * 2:
                return [left_margin, left_margin + TAB_STOP_WIDTH]
    return guess_left_margin_for_misc_document(counts)


def guess_left_margin(pdf_file: pdfplumber.PDF, lines: List[List[Word]]) -> List[float]:
    words_x0: List[int] = [
        # assume line position is same for all words in line
        # hence just use the first word
        round(line[0]["x0"])
        for line in lines
    ]
    counts = [(x0, words_x0.count(x0)) for x0 in set(words_x0)]

    is_a4_document = len(
        [True for page in pdf_file.pages if is_a4_page(page)]
    ) >= 0.9 * len(pdf_file.pages)
    if is_a4_document:
        return guess_left_margin_for_a4_document(counts)
    else:
        return guess_left_margin_for_misc_document(counts)


def dict_list_unique_by(dict_list, func):
    return list({func(item): item for item in dict_list}.values())


def print_runtime(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        print(f"Function {func.__name__} finished in {end_time - start_time}s")
        return result

    return wrapper


def pretty_print(value):
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(value)


def contains_alphanumeric(string):
    return len(re.sub(r"\W+", "", string)) > 0
