from numbers import Number
import pdfplumber
from typing import List, Tuple
from pdf_scout.logger import debug_log
from pdf_scout.types import Word
import statistics


A4 = {"width": 21, "height": 29.7}
A4_COMMON_LEFT_MARGINS = [1.27, 1.9, 2.54, 3.18]
TAB_STOP_WIDTH = 1.27


def points_to_cm(points: Number):
    return points / 72 * 2.54


def cm_to_points(cm: Number):
    return cm * 72 / 2.54


def is_a4_page(page) -> bool:
    return (
        round(points_to_cm(page.width), 1) == A4["width"]
        and round(points_to_cm(page.height), 1) == A4["height"]
    )


def guess_left_margin_for_misc_document(
    counts: List[Tuple[Number, int]]
) -> List[Number]:
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


def guess_left_margin_for_a4_document(counts: List[Tuple[Number, int]]) -> List[Number]:
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


def guess_left_margin(pdf_file: pdfplumber.PDF, words: List[Word]) -> List[Number]:
    words_x0 = [round(word["x0"]) for word in words]
    counts = [(x0, words_x0.count(x0)) for x0 in set(words_x0)]

    is_a4_document = len(
        [True for page in pdf_file.pages if is_a4_page(page)]
    ) >= 0.9 * len(pdf_file.pages)
    if is_a4_document:
        return guess_left_margin_for_a4_document(counts)
    else:
        return guess_left_margin_for_misc_document(counts)
