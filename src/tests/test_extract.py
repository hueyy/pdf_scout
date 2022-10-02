from app import open_pdf_file
from extract import (
    guess_body_spacing,
    raw_extract_words,
    guess_body_font_size,
    add_line_spacing_to_words,
)

INPUT_FILES = [
    "./pdf/Law Society of Singapore v Loh Wai Mun Daniel [2004] SGHC 36 - Judgment.pdf",
    "./pdf/RecordTV Pte Ltd v MediaCorp TV Singapore Pte Ltd and others [2010] SGCA 43 - Judgment.pdf",
]


def test_raw_extract_words(snapshot):
    for file_path in INPUT_FILES:
        file = open_pdf_file(file_path)
        output = raw_extract_words(file)
        snapshot.assert_match(output)


def test_guess_body_font_size(snapshot):
    for file_path in INPUT_FILES:
        file = open_pdf_file(file_path)
        all_words = raw_extract_words(file)
        body_font_size = guess_body_font_size(all_words)
        snapshot.assert_match(body_font_size)


def test_guess_body_spacing(snapshot):
    for file_path in INPUT_FILES:
        file = open_pdf_file(file_path)
        all_words = raw_extract_words(file)
        all_words = add_line_spacing_to_words(file, all_words)
        body_spacing = guess_body_spacing(all_words)
        snapshot.assert_match(body_spacing)
