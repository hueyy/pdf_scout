from pdf_scout.extract import extract_all_lines
from pdf_scout.scoring import score_paragraphs
from pdf_scout.bookmarks import generate_bookmarks, write_bookmarks
from pdf_scout.custom_types import HeadingScore, Word
from pdf_scout.paragraphs import group_lines_in_paragraphs
from time import time
from typing import List, Tuple
from operator import itemgetter
import pdfplumber
import typer


def get_top_scored_paragraphs(
    scored_paragraphs: List[Tuple[HeadingScore, List[List[Word]]]],
    levels: int
) -> List[Tuple[int, List[List[Word]]]]:
    all_scores = list(set([score["overall"] for score, _ in scored_paragraphs]))
    all_scores.sort(reverse=True)
    top_scores: List[float] = all_scores[0:levels]
    top_scored_paragraphs: List[Tuple[int, List[List[Word]]]] = [
        (top_scores.index(score["overall"]), paragraph)
        for score, paragraph in scored_paragraphs
        if score["overall"] in top_scores
    ]
    return top_scored_paragraphs


def main(
    input_file_path: str,
    output_file_path: str = typer.Argument(""),
    levels: int = typer.Argument(3),
) -> None:
    start_time = time()

    if input_file_path is None or len(input_file_path) == 0:
        print("Error: file_path not provided")
        raise typer.Exit(code=1)

    if len(output_file_path) == 0:
        input_path_start, _ = input_file_path.split(".pdf")
        output_file_path = f"{input_path_start}-out.pdf"

    pdf_file = pdfplumber.open(input_file_path)
    all_lines, heading_lines = itemgetter("all_lines", "heading_lines")(
        extract_all_lines(pdf_file)
    )
    heading_paragraphs = group_lines_in_paragraphs(heading_lines)
    scored_paragraphs = score_paragraphs(all_lines, heading_paragraphs)
    top_scored_paragraphs = get_top_scored_paragraphs(scored_paragraphs, levels)

    bookmarks = generate_bookmarks(pdf_file, top_scored_paragraphs)
    pdf_file.close()

    write_bookmarks(input_file_path, output_file_path, bookmarks)

    end_time = time()
    print(f"Finished in {end_time - start_time}s")


def start() -> None:
    typer.run(main)


if __name__ == "__main__":
    start()
