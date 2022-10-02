from itertools import groupby
from numbers import Number
from operator import itemgetter
from typing import List, Tuple
from pdf_scout.logger import debug_log
import statistics


def guess_left_margin(words) -> List[Number]:
    words_x0 = [round(word["x0"]) for word in words]
    counts = [(x0, words_x0.count(x0)) for x0 in set(words_x0)]
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


def add_line_spacing_to_words(pdf_file, all_words):
    # add distance from previous & next line
    # assumes all lines are perfectly horizontal and of full width
    line_positions: List[Tuple[int, List[Number]]] = [
        (
            page_number,
            sorted(list(set([get_word_line_position(word) for word in words]))),
        )
        for page_number, words in groupby(all_words, key=itemgetter("page_number"))
    ]
    return [
        add_line_spacing_to_word(line_positions, word, pdf_file) for word in all_words
    ]


def guess_body_spacing(words) -> Tuple[Number, Number]:
    return (
        statistics.mode([word["top_spacing"] for word in words]),
        statistics.mode([word["bottom_spacing"] for word in words]),
    )


def get_word_line_position(word) -> Number:
    return word["top"]


def add_line_spacing_to_word(
    line_positions: List[Tuple[int, List[Number]]], word, pdf_file
):
    page_line_positions = [
        page_lines
        for page_number, page_lines in line_positions
        if page_number == word["page_number"]
    ][0]
    index = page_line_positions.index(get_word_line_position(word))
    cur_line_position = page_line_positions[index]
    prev_line_position = page_line_positions[index - 1] if index != 0 else 0
    next_line_position = (
        page_line_positions[index + 1]
        if index < len(page_line_positions) - 1
        else pdf_file.pages[word["page_number"] - 1].height
    )
    return dict(
        **word,
        top_spacing=round(cur_line_position - prev_line_position, 2),
        bottom_spacing=round(next_line_position - cur_line_position, 2),
    )


def raw_extract_words(pdf_file) -> List[dict[str, any]]:
    all_words = [
        word
        for page_list in (
            [
                dict(**word, page_number=page.page_number)
                for word in page.extract_words(
                    keep_blank_chars=True,
                    use_text_flow=True,
                    extra_attrs=["fontname", "size"],
                )
            ]
            for page in pdf_file.pages
        )
        for word in page_list
    ]
    return all_words


def extract_all_words(pdf_file) -> List[dict[str, any]]:
    all_words = raw_extract_words(pdf_file)
    all_words = add_line_spacing_to_words(pdf_file, all_words)

    body_top_spacing, body_bottom_spacing = guess_body_spacing(all_words)

    # TODO: add some margin of appreciation to account for indented headers, footnotes, etc
    # TODO: handle center-aligned text
    left_margins = guess_left_margin(all_words)

    non_body_words = [
        word
        for word in all_words
        if (
            (
                # ignore all words with normal paragraph spacing
                # 5% because line spacing is not always precise
                word["top_spacing"] >= body_top_spacing * 1.05
                and word["bottom_spacing"] >= body_bottom_spacing * 1.05
            )
            and (  # ignore all words not at left margin
                round(word["x0"]) in left_margins
            )
        )
    ]

    debug_log("extract_all_words locals: ", locals())

    return all_words, non_body_words
