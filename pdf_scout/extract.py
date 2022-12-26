from itertools import groupby
from operator import itemgetter
from typing import List, Tuple
from pdf_scout.logger import debug_log
from pdf_scout.custom_types import RawWord, Word, DocumentWords, Rect
from pdf_scout.utils import guess_left_margin, dict_list_unique_by
import statistics
import pdfplumber
import math
from unidecode import unidecode
from functools import reduce


def get_header_bottom_position(pdf_file: pdfplumber.PDF) -> float:
    HEADER_POSITION_THRESHOLD = 0.2  # assume header is in top 20% of page
    HEADER_COUNT_THRESHOLD = 0.7  # assume header is on >70% of pages

    # check if rectangle header
    header_rects: List[List[Rect]] = [
        [
            rect
            for rect in page.rects
            if (
                rect["height"] > 0
                and rect["width"] > 0
                and rect["bottom"] <= HEADER_POSITION_THRESHOLD * page.height
            )
        ]
        for page in pdf_file.pages
    ]
    is_rectangle_header = len(
        [True for rects_in_page in header_rects if len(rects_in_page) >= 1]
    ) >= HEADER_COUNT_THRESHOLD * len(pdf_file.pages)

    if is_rectangle_header:
        return statistics.mode(
            [rect["bottom"] for rects_in_page in header_rects for rect in rects_in_page]
        )
    else:
        return 0


def get_footer_top_position(pdf_file: pdfplumber.PDF):
    FOOTER_POSITION_THRESHOLD = 0.2  # assume footer is in bottom 20% of page
    FOOTER_COUNT_THRESHOLD = 0.7  # assume footer is on >70% of pages
    # TODO
    return None


def get_sorted_unique_line_positions(words_in_page: List[RawWord]):
    raw_line_positions = [get_word_line_position(word) for word in words_in_page]
    return sorted(
        list(dict_list_unique_by(raw_line_positions, lambda x: f"{x[0],x[1]}")),
        key=lambda x: x[0],
    )


def add_line_spacing_to_words(
    pdf_file: pdfplumber.PDF, all_words: List[RawWord]
) -> List[Word]:
    # add distance from previous & next line
    # assumes all lines are perfectly horizontal and of full width
    line_positions: List[Tuple[int, List[Tuple[float, float]]]] = [
        (page_number, get_sorted_unique_line_positions(words))
        for page_number, words in groupby(all_words, key=itemgetter("page_number"))
    ]
    return [
        add_line_spacing_to_word(line_positions, word, pdf_file) for word in all_words
    ]


def guess_body_spacing(words: List[Word]) -> float:
    return min(
        statistics.mode([word["top_spacing"] for word in words]),
        statistics.mode([word["bottom_spacing"] for word in words]),
    )


def guess_body_font(words: List[Word]):
    return statistics.mode([word["fontname"] for word in words])


def guess_body_font_size(words: List[Word]):
    return statistics.mode([word["size"] for word in words])


def get_word_line_position(word: RawWord) -> Tuple[float, float]:
    return word["top"], word["bottom"]


def add_line_spacing_to_word(
    # Adds top_spacing and bottom_spacing to dict.
    line_positions: List[Tuple[int, List[Tuple[float, float]]]],
    word: RawWord,
    pdf_file: pdfplumber.PDF,
) -> Word:
    page_line_positions = [
        page_lines
        for page_number, page_lines in line_positions
        if page_number == word["page_number"]
    ][0]
    cur_top, cur_bottom = get_word_line_position(word)
    index = [
        i
        for i, (top, bottom) in enumerate(page_line_positions)
        if top == cur_top and bottom == cur_bottom
    ][0]
    prev_top, prev_bottom = page_line_positions[index - 1] if index != 0 else (0, 0)
    next_top, next_bottom = (
        page_line_positions[index + 1]
        if index < len(page_line_positions) - 1
        else (
            pdf_file.pages[word["page_number"] - 1].height,
            pdf_file.pages[word["page_number"] - 1].height,
        )
    )
    return {
        **word,
        "top_spacing": round(cur_top - prev_bottom, 2),
        "bottom_spacing": round(next_top - cur_bottom, 2),
    }


def raw_extract_words(
    pdf_file: pdfplumber.PDF, header_bottom_position: float = 0
) -> List[RawWord]:
    all_words = [
        word
        for page_list in (
            [
                {**word, "text": unidecode(word["text"]).strip(), "page_number": page.page_number}
                for word in page.extract_words(
                    keep_blank_chars=True,
                    use_text_flow=True,
                    extra_attrs=["fontname", "size"],
                )
            ]
            for page in pdf_file.pages
        )
        for word in page_list
        if (
            (len(word["text"]) > 0)  # ignore all words that are just whitespace
            and word["top"] > header_bottom_position  # ignore header
        )
    ]
    
    # combine words on the same line
    all_words_in_lines = []
    same_line = lambda prev, cur: (
        cur["top"] == prev["top"] and
        cur["bottom"] == prev["bottom"] and
        cur["fontname"] == prev["fontname"] and
        cur["size"] == prev["size"] and 
        cur["page_number"] == prev["page_number"]
    )
    for index, raw_word in enumerate(all_words):
        if index == 0:
            all_words_in_lines.append(raw_word)
        if same_line(all_words[index - 1], raw_word):
            all_words_in_lines[-1] = {
                **all_words_in_lines[-1],
                "text": all_words_in_lines[-1]["text"] + " " + raw_word["text"]
            }
        else:
            all_words_in_lines.append(raw_word)

    return all_words_in_lines


def get_heading_words(all_words: List[Word], left_margins: List[float]) -> List[Word]:
    body_font = guess_body_font(all_words)
    body_font_size = guess_body_font_size(all_words)

    body_spacing = guess_body_spacing(all_words)

    return [
        word
        for word in all_words
        if (
            (
                not ( # same font as body (and not bold / italic) and same font size as body
                    word["fontname"] == body_font
                    and math.isclose(word["size"], body_font_size, rel_tol=0.01)
                )
            )
            and not (  # same font size as body and same spacing as body
                math.isclose(word["size"], body_font_size, rel_tol=0.01)
                and (
                    math.isclose(word["top_spacing"], body_spacing, rel_tol=0.05)
                    or math.isclose(word["bottom_spacing"], body_spacing, rel_tol=0.05)
                )
            )
            and (  # ignore all words not at left margin
                round(word["x0"], None) in left_margins
            )
        )
    ]


def extract_all_words(pdf_file: pdfplumber.PDF) -> DocumentWords:

    header_bottom_position = get_header_bottom_position(pdf_file)

    raw_words = raw_extract_words(pdf_file, header_bottom_position)
    all_words_with_line_spacing = add_line_spacing_to_words(pdf_file, raw_words)

    # TODO: add some margin of appreciation to account for indented headers, footnotes, etc
    # TODO: handle center-aligned text
    left_margins = guess_left_margin(pdf_file, all_words_with_line_spacing)

    heading_words_with_line_spacing = get_heading_words(
        all_words_with_line_spacing, left_margins
    )

    debug_log("extract_all_words locals: ", locals())

    return {
        "all_words": all_words_with_line_spacing,
        "heading_words": heading_words_with_line_spacing,
    }
