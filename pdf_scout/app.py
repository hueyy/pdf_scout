from pdf_scout.extract import extract_all_lines
from pdf_scout.scoring import score_paragraphs
from pdf_scout.bookmarks import generate_bookmarks, write_bookmarks
from pdf_scout.custom_types import HeadingScore, Word, Bookmark
from pdf_scout.paragraphs import group_lines_in_paragraphs
from pdf_scout.utils import print_runtime, pretty_print
from typing import List, Tuple
from operator import itemgetter
import pdfplumber
import typer

app = typer.Typer()

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

@app.command()
def extract_all_heading_lines(
    input_file_path: str,
    ctx: typer.Context = None
) -> Tuple[List[List[Word]], List[List[Word]]]:
    pdf_file = pdfplumber.open(input_file_path)
    all_lines, heading_lines = itemgetter("all_lines", "heading_lines")(
        extract_all_lines(pdf_file)
    )
    if ctx is not None and ctx.command.name == 'extract-all-heading-lines':
        pretty_print(all_lines, heading_lines)
    else:
        pretty_print(ctx)
    return all_lines, heading_lines

@app.command()
def extract_all_heading_paragraphs(
    input_file_path: str,
    ctx: typer.Context = None
) -> List[List[List[Word]]]:
    all_lines, heading_lines = extract_all_heading_lines(ctx, input_file_path)
    heading_paragraphs = group_lines_in_paragraphs(heading_lines)
    if ctx is not None and ctx.command.name == 'extract-all-heading-paragraphs':
        pretty_print(heading_paragraphs)
    return heading_paragraphs

@app.command()
def generate_toc(
    input_file_path: str,
    levels: int = typer.Argument(3),
    ctx: typer.Context = None,
) -> List[Tuple[int, Bookmark]]:
    heading_paragraphs = extract_all_heading_paragraphs(ctx, input_file_path)
    scored_paragraphs = score_paragraphs(all_lines, heading_paragraphs)
    top_scored_paragraphs = get_top_scored_paragraphs(scored_paragraphs, levels)
    bookmarks = generate_bookmarks(pdf_file, top_scored_paragraphs)
    pdf_file.close()
    if ctx is not None and ctx.command.name == 'generate-toc':
        pretty_print(bookmarks)
    return bookmarks

@print_runtime
@app.command()
def add_bookmarks(
    input_file_path: str,
    output_file_path: str = typer.Argument(""),
    levels: int = typer.Argument(3),
) -> None:
    if input_file_path is None or len(input_file_path) == 0:
        print("Error: file_path not provided")
        raise typer.Exit(code=1)

    if len(output_file_path) == 0:
        input_path_start, _ = input_file_path.split(".pdf")
        output_file_path = f"{input_path_start}-out.pdf"

    bookmarks = toc(input_file_path, levels)

    write_bookmarks(input_file_path, output_file_path, bookmarks)

if __name__ == "__main__":
    app()
