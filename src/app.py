from collections import Counter
from itertools import groupby
from numbers import Number
from operator import itemgetter
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from typing import List, TypedDict
from typing import Optional
import pdfplumber
import re
import sys
import typer
from pprint import pprint


# def group_chars_by_attr(attr: str, chars, sort=False):
#     get_attr = itemgetter(attr)
#     if sort:
#         chars.sort(key=get_attr)
#     return [[key, [char for char in val]] for key, val in groupby(chars, key=get_attr)]


# def group_chars_by_line(chars):
#     return group_chars_by_attr(attr="bottom", chars=chars, sort=True)


def guess_left_margin(words) -> Number:
    return Counter(map(lambda w: w["x0"], words)).most_common(1)[0][0]


def score_font_name(font_name: str) -> Number:
    if re.match(r"-Bold$", font_name):
        return 10
    if re.match(r"-Oblique", font_name):
        return 5
    return 0


def score_font_size(font_size: Number) -> Number:
    # TODO: make more sophisticated; steps should be exponential
    return font_size


def get_heading_score(word) -> Number:
    font_name: str = word["fontname"]
    font_size: Number = word["size"]

    score = score_font_name(font_name) + score_font_size(font_size)
    return score


class Bookmark(TypedDict):
    title: str
    page_number: str
    scroll_distance: Number


def write_bookmarks(
    input_path: str, output_path: str, bookmarks: List[Bookmark]
) -> None:
    merger = PdfMerger()
    merger.append(input_path)
    for bookmark in bookmarks:
        merger.add_outline_item(
            bookmark["title"],
            bookmark["page_number"] - 1,
            None,
            None,
            False,
            False,
            "/FitH",
            bookmark["scroll_distance"],
        )
    merger.write(output_path)
    merger.close()
    return None


def extract_all_words(pdf_file):
    return [
        word
        for page_list in (
            [
                dict(**word, page_number=page.page_number)
                for word in page.extract_words(
                    keep_blank_chars=True, extra_attrs=["fontname", "size"]
                )
            ]
            for page in pdf_file.pages
        )
        for word in page_list
    ]


def add_bookmarks_to_pdf(input_path: str, output_path: str = "", headings=5):
    if len(output_path) == 0:
        input_path_start, _ = input_path.split(".pdf")
        output_path = f"{input_path_start}-out.pdf"
    with pdfplumber.open(input_path) as pdf_file:
        all_words = extract_all_words(pdf_file)
        left_margin = guess_left_margin(all_words)
        # TODO: add some margin of appreciation to account for indented headers, footnotes, etc

        all_words = list(filter(lambda w: w["x0"] == left_margin, all_words))

        # pprint(all_words)

        # all_fonts = set(map(lambda w: w["fontname"], all_words))
        # all_font_sizes = set(map(lambda w: w["size"], all_words))

        scored_words = [[get_heading_score(word), word] for word in all_words]
        top_scores = sorted(
            list(set([score for score, _ in scored_words])), reverse=True
        )[0:headings]
        top_scored_words = list(filter(lambda tup: tup[0] in top_scores, scored_words))

        pprint(top_scored_words)

        bookmarks: List[Bookmark] = [
            dict(
                title=word["text"],
                page_number=word["page_number"],
                scroll_distance=(
                    pdf_file.pages[word["page_number"] - 1].height
                    - word["top"]
                    + word["bottom"]
                    - word["top"]
                ),
            )
            for _, word in top_scored_words
        ]

        pprint(bookmarks)

        write_bookmarks(input_path, output_path, bookmarks)


def main(input_file_path: str, output_file_path: Optional[str] = typer.Argument("")):
    if input_file_path is None or len(input_file_path) == 0:
        print("Error: file_path not provided")
        raise typer.Exit(code=1)
    add_bookmarks_to_pdf(input_file_path, output_file_path)


if __name__ == "__main__":
    typer.run(main)
