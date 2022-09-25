from collections import Counter
from numbers import Number
from PyPDF2 import PdfMerger
from typing import List, Tuple, TypedDict
from typing import Optional
import pdfplumber
import re
import typer
from pprint import pprint


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


def find_last_list(input_list):
    if len(input_list) == 0:
        return input_list
    if isinstance(input_list[-1], list):
        return find_last_list(input_list[-1])
    else:
        return input_list


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
                parent_bookmarks.pop()
                parent_bookmark = get_last_bookmark(parent_bookmarks)
                new_bookmark = add_bookmark(parent_bookmark)

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


def generate_bookmarks(top_scored_words, pages):
    last_rank = 0
    result = []
    current_level = 0
    for rank, word in top_scored_words:
        bookmark = []
        if rank > last_rank:
            current_level += 1
            find_last_list(result).append(bookmark)
        elif rank < last_rank:
            current_level -= 1
            entrypoint = result
            for i in range(current_level):
                entrypoint = entrypoint[-1]
            entrypoint.extend(bookmark)
        else:
            find_last_list(result).extend(bookmark)
        last_rank = rank
    return result


def add_bookmarks_to_pdf(input_path: str, output_path: str = "", levels=5):
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
        )[0:levels]
        top_scored_words = [
            [top_scores.index(score), word]
            for score, word in scored_words
            if score in top_scores
        ]

        pprint(top_scored_words)

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

        pprint(bookmarks)

        write_bookmarks(input_path, output_path, bookmarks)


def main(input_file_path: str, output_file_path: Optional[str] = typer.Argument("")):
    if input_file_path is None or len(input_file_path) == 0:
        print("Error: file_path not provided")
        raise typer.Exit(code=1)
    add_bookmarks_to_pdf(input_file_path, output_file_path)


if __name__ == "__main__":
    typer.run(main)
