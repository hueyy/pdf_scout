from numbers import Number
from PyPDF2 import PdfMerger
from rich import print as rprint
from scoring import get_heading_score, HeadingScore
from typing import List, Tuple, TypedDict
from typing import Optional
import pdfplumber
import statistics
import typer
from itertools import groupby
from operator import itemgetter


def guess_left_margin(words) -> Number:
    # TODO: set max thresholds to handle for documents with a lot of indented text
    return statistics.mode([word["x0"] for word in words])


def guess_body_score(word_list: Tuple[HeadingScore, any]) -> Number:
    return statistics.mode([score["font"] for score, _ in word_list])


def guess_body_spacing(words) -> Tuple[Number, Number]:
    return (
        statistics.mode([word["top_spacing"] for word in words]),
        statistics.mode([word["bottom_spacing"] for word in words]),
    )


class Bookmark(TypedDict):
    title: str
    page_number: str
    scroll_distance: Number


def write_bookmarks(
    input_path: str, output_path: str, bookmarks: List[Bookmark]
) -> None:
    merger = PdfMerger()
    merger.append(input_path, import_outline=False)  # disregard existing outline

    parent_bookmarks: List[Tuple(int, any)] = []
    # last item in list is last outline item added

    add_bookmark_to_writer = lambda writer, bookmark, parent: writer.add_outline_item(
        bookmark["title"],
        bookmark["page_number"] - 1,
        parent,
        None,
        False,
        False,
        "/FitH",
        bookmark["scroll_distance"],
    )
    get_last_bookmark = (
        lambda parent_bs: parent_bs[-1][1] if len(parent_bs) >= 1 else None
    )

    for rank, bookmark in bookmarks:
        add_bookmark = lambda p: add_bookmark_to_writer(merger, bookmark, p)
        rprint(rank, bookmark["title"])

        if len(parent_bookmarks) == 0:
            new_bookmark = add_bookmark(None)
            parent_bookmarks.append((rank, new_bookmark))
        else:
            last = parent_bookmarks[-1]
            last_rank, last_bookmark = last
            if last_rank < rank:
                new_bookmark = add_bookmark(last_bookmark)
                parent_bookmarks.append((rank, new_bookmark))
            elif last_rank == rank:
                parent_bookmarks.pop()
                parent_bookmark = get_last_bookmark(parent_bookmarks)
                new_bookmark = add_bookmark(parent_bookmark)
                parent_bookmarks.append((rank, new_bookmark))
            elif last_rank > rank:
                parent_bookmarks.pop()
                if len(parent_bookmarks) >= 1:
                    parent_bookmarks.pop()
                parent_bookmark = get_last_bookmark(parent_bookmarks)
                new_bookmark = add_bookmark(parent_bookmark)

    merger.write(output_path)
    merger.close()
    return None


def get_word_line_position(word) -> Number:
    return word["top"]


def add_line_spacing(line_positions: List[Tuple[int, List[Number]]], word, pdf_file):
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


def extract_all_words(pdf_file) -> List[dict[str, any]]:
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

    # add distance from previous & next line
    # assumes all lines are perfectly horizontal and of full width
    line_positions: List[Tuple[int, List[Number]]] = [
        (
            page_number,
            sorted(list(set([get_word_line_position(word) for word in words]))),
        )
        for page_number, words in groupby(all_words, key=itemgetter("page_number"))
    ]
    all_words = [add_line_spacing(line_positions, word, pdf_file) for word in all_words]
    # ignore all words with normal paragraph spacing
    body_top_spacing, body_bottom_spacing = guess_body_spacing(all_words)
    all_words = [
        word
        for word in all_words
        if (
            word["top_spacing"] != body_top_spacing
            and word["bottom_spacing"] != body_bottom_spacing
        )
    ]

    # ignore all words not at left margin
    left_margin = guess_left_margin(all_words)
    # TODO: add some margin of appreciation to account for indented headers, footnotes, etc
    # TODO: handle center-aligned text
    all_words = [word for word in all_words if word["x0"] == left_margin]

    return all_words


def score_words(all_words: List[any]):
    scored_words: List[Tuple[HeadingScore, any]] = [
        (get_heading_score(word), word) for word in all_words
    ]
    body_score = guess_body_score(scored_words)
    # ignore all body text
    scored_words = [
        (score, word) for score, word in scored_words if score["font"] != body_score
    ]
    return scored_words


def add_bookmarks_to_pdf(input_path: str, output_path: str = "", levels=3):
    if len(output_path) == 0:
        input_path_start, _ = input_path.split(".pdf")
        output_path = f"{input_path_start}-out.pdf"
    with pdfplumber.open(input_path) as pdf_file:
        all_words = extract_all_words(pdf_file)
        scored_words = score_words(all_words)

        top_scores: List[Number] = sorted(
            list(set([score["overall"] for score, _ in scored_words])), reverse=True
        )[0:levels]
        top_scored_words = [
            [top_scores.index(score["overall"]), word]
            for score, word in scored_words
            if score["overall"] in top_scores
        ]
        rprint(top_scored_words)

        bookmarks: List[Tuple[int, Bookmark]] = [
            (
                rank,
                dict(
                    title=word["text"],
                    page_number=word["page_number"],
                    scroll_distance=(
                        pdf_file.pages[word["page_number"] - 1].height
                        - word["top"]
                        + word["bottom"]
                        - word["top"]
                    ),
                ),
            )
            for rank, word in top_scored_words
        ]

        write_bookmarks(input_path, output_path, bookmarks)


def main(input_file_path: str, output_file_path: Optional[str] = typer.Argument("")):
    if input_file_path is None or len(input_file_path) == 0:
        print("Error: file_path not provided")
        raise typer.Exit(code=1)
    add_bookmarks_to_pdf(input_file_path, output_file_path)


if __name__ == "__main__":
    typer.run(main)
