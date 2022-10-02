from numbers import Number
from pdf_scout.extract import extract_all_words
from pdf_scout.scoring import score_words
from pdf_scout.logger import debug_log
from PyPDF2 import PdfMerger
from time import time
from typing import List, Tuple, TypedDict
from typing import Optional
import pdfplumber
import typer


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

        debug_log("Rank: ", rank, bookmark["title"])

        if len(parent_bookmarks) == 0:
            new_bookmark = add_bookmark(None)
        else:
            last_rank, last_bookmark = parent_bookmarks[-1]
            if last_rank < rank:
                new_bookmark = add_bookmark(last_bookmark)
            else:
                parent_bookmarks.pop()
                if last_rank == rank:
                    parent_bookmark = get_last_bookmark(parent_bookmarks)
                    new_bookmark = add_bookmark(parent_bookmark)
                elif last_rank > rank:
                    rank_difference = last_rank - rank
                    for _ in range(rank_difference):
                        if len(parent_bookmarks) >= 1:
                            parent_bookmarks.pop()
                    parent_bookmark = get_last_bookmark(parent_bookmarks)
                    new_bookmark = add_bookmark(parent_bookmark)
        parent_bookmarks.append((rank, new_bookmark))

    merger.write(output_path)
    merger.close()
    return None


def open_pdf_file(input_path: str) -> pdfplumber.PDF:
    return pdfplumber.open(input_path)


def add_bookmarks_to_pdf(input_path: str, output_path: str = "", levels=3):
    if len(output_path) == 0:
        input_path_start, _ = input_path.split(".pdf")
        output_path = f"{input_path_start}-out.pdf"

    pdf_file = open_pdf_file(input_path)
    all_words, non_body_words = extract_all_words(pdf_file)
    scored_words = score_words(all_words, non_body_words)

    top_scores: List[Number] = sorted(
        list(set([score["overall"] for score, _ in scored_words])), reverse=True
    )[0:levels]
    top_scored_words = [
        [top_scores.index(score["overall"]), word]
        for score, word in scored_words
        if score["overall"] in top_scores
    ]

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

    debug_log("add_bookmarks_to_pdf locals: ", locals())

    write_bookmarks(input_path, output_path, bookmarks)

    pdf_file.close()


def main(input_file_path: str, output_file_path: Optional[str] = typer.Argument("")):
    start_time = time()
    if input_file_path is None or len(input_file_path) == 0:
        print("Error: file_path not provided")
        raise typer.Exit(code=1)
    add_bookmarks_to_pdf(input_file_path, output_file_path)
    end_time = time()
    print(f"Finished in {end_time - start_time}s")


def start():
    typer.run(main)


if __name__ == "__main__":
    start()
