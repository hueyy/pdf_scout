from itertools import groupby
from typing import List, Tuple, Iterator
from pdf_scout.logger import debug_log
from pdf_scout.custom_types import RawWord, Word, DocumentLines, Rect
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
            rect  # type: ignore
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


def get_sorted_unique_line_positions(
    lines: Iterator[List[RawWord]],
) -> List[Tuple[float, float]]:
    raw_line_positions: List[Tuple[float, float]] = [
        # assume line position is same for all words in line
        # hence just use the first word
        # get_word_line_position(line[0])
        # use min top and max bottom for situations where
        # pdfplumber extracts two lines of text as a single line
        (min([word["top"] for word in line]), max([word["bottom"] for word in line]))
        # statistics.mode([
        #     get_word_line_position(word) for word in line
        # ])
        for line in lines
    ]
    return sorted(
        list(dict_list_unique_by(raw_line_positions, lambda x: f"{x[0],x[1]}")),
        key=lambda x: x[0],
    )


def add_line_spacing_to_lines(
    pdf_file: pdfplumber.PDF, lines: List[List[RawWord]]
) -> List[List[Word]]:
    # add distance from previous & next line
    # assumes all lines are perfectly horizontal and of full width
    line_positions: List[Tuple[int, List[Tuple[float, float]]]] = [
        (page_number, get_sorted_unique_line_positions(lines_in_page))
        for page_number, lines_in_page in groupby(
            lines, key=lambda l: l[0]["page_number"]
        )
    ]
    return [
        [add_line_spacing_to_word(line_positions, word, pdf_file) for word in line]
        for line in lines
    ]


def guess_body_spacing(lines: List[List[Word]]) -> float:
    return min(
        statistics.mode([word["top_spacing"] for line in lines for word in line]),
        statistics.mode([word["bottom_spacing"] for line in lines for word in line]),
    )


def guess_body_font(lines: List[List[Word]]):
    return statistics.mode([word["fontname"] for line in lines for word in line])


def guess_body_font_size(lines: List[List[Word]]):
    return statistics.mode([word["size"] for line in lines for word in line])


def get_word_line_position(word: RawWord) -> Tuple[float, float]:
    return word["top"], word["bottom"]


def add_line_spacing_to_word(
    # Adds top_spacing and bottom_spacing to dict.
    line_positions: List[Tuple[int, List[Tuple[float, float]]]],
    word: RawWord,
    pdf_file: pdfplumber.PDF,
) -> Word:
    page_line_positions: List[Tuple[float, float]] = [
        lines_in_page
        for page_number, lines_in_page in line_positions
        if page_number == word["page_number"]
    ][0]
    cur_top, cur_bottom = get_word_line_position(word)
    index = next(
        i
        for i, (top, bottom) in enumerate(page_line_positions)
        if top == cur_top and bottom == cur_bottom
    )
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
        **word,  # type: ignore
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
                {
                    **word,
                    "text": unidecode(word["text"]).strip(),
                    "page_number": int(page.page_number),
                }
                for word in page.extract_words(
                    keep_blank_chars=True,
                    use_text_flow=True,
                    extra_attrs=["fontname", "size", "bottom"],
                )
            ]
            for page in pdf_file.pages
        )
        for word in page_list
        if (
            (len(str(word["text"])) > 0)  # ignore all words that are just whitespace
            and float(str(word["top"])) > header_bottom_position  # ignore header
        )
    ]

    # merge text with identical formatting
    all_words_merged = []
    is_same_formatting = lambda prev, cur: (
        cur["bottom"] == prev["bottom"]
        and cur["fontname"] == prev["fontname"]
        and cur["size"] == prev["size"]
        and cur["page_number"] == prev["page_number"]
    )
    for index, raw_word in enumerate(all_words):
        if index == 0:
            all_words_merged.append(raw_word)
        if is_same_formatting(all_words[index - 1], raw_word):
            all_words_merged[-1] = {
                **all_words_merged[-1],  # type: ignore
                "text": str(all_words_merged[-1]["text"]) + " " + str(raw_word["text"]),
            }
        else:
            all_words_merged.append(raw_word)

    return all_words_merged  # type: ignore


def get_heading_lines(
    lines: List[List[Word]], left_margins: List[float]
) -> List[List[Word]]:
    body_font = guess_body_font(lines)
    body_font_size = guess_body_font_size(lines)

    body_spacing = guess_body_spacing(lines)

    return [
        line
        for line in lines
        if (
            (
                not any(
                    [
                        # same font as body (and not bold / italic)
                        # and same font size as body
                        word["fontname"] == body_font
                        and math.isclose(word["size"], body_font_size, rel_tol=0.01)
                        for word in line
                    ]
                )
            )
            and not any(
                [
                    # same font size as body and same spacing as body
                    math.isclose(word["size"], body_font_size, rel_tol=0.01)
                    and (
                        math.isclose(word["top_spacing"], body_spacing, rel_tol=0.05)
                        or math.isclose(
                            word["bottom_spacing"], body_spacing, rel_tol=0.05
                        )
                    )
                    for word in line
                ]
            )
            and (  # ignore all words not at left margin
                round(line[0]["x0"], None) in left_margins
            )
        )
    ]


def words_to_lines(raw_words: List[RawWord]) -> List[List[RawWord]]:
    """
    takes a list of words and returns a list of lists,
    each list representing a line and containing words
    that are on the same line as visually represented in the document
    """

    def to_list(
        acc: List[List[RawWord]],
        cur: RawWord,
    ):
        if len(acc) == 0:
            return acc + [[cur]]
        elif (
            cur["bottom"] == acc[-1][0]["bottom"]
            and cur["page_number"] == acc[-1][0]["page_number"]
        ):
            return [*acc[:-1], [*acc[-1], cur]]
        else:
            return acc + [[cur]]

    return reduce(to_list, raw_words, [])


def extract_all_lines(pdf_file: pdfplumber.PDF) -> DocumentLines:

    header_bottom_position = get_header_bottom_position(pdf_file)

    raw_words = raw_extract_words(pdf_file, header_bottom_position)
    lines = words_to_lines(raw_words)
    all_lines_with_line_spacing = add_line_spacing_to_lines(pdf_file, lines)

    # TODO: add some margin of appreciation to account for indented headers, footnotes, etc
    # TODO: handle center-aligned text
    left_margins = guess_left_margin(pdf_file, all_lines_with_line_spacing)

    heading_lines_with_line_spacing = get_heading_lines(
        all_lines_with_line_spacing, left_margins
    )

    return {
        "all_lines": all_lines_with_line_spacing,
        "heading_lines": heading_lines_with_line_spacing,
    }
