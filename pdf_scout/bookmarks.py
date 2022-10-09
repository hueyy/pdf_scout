from PyPDF2 import PdfMerger
from typing import Any, List, Tuple
from pdf_scout.logger import debug_log
from pdf_scout.types import Word, Bookmark
import pdfplumber


def write_bookmarks(
    input_path: str, output_path: str, bookmarks: List[Tuple[int, Bookmark]]
) -> None:
    merger = PdfMerger()
    merger.append(input_path, import_outline=False)  # disregard existing outline

    parent_bookmarks: List[Tuple[int, Any]] = []
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
    return


def generate_bookmarks(
    pdf_file: pdfplumber.PDF, top_scored_words: List[Tuple[int, Word]]
):
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

    return bookmarks
