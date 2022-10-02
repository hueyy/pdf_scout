from pdf_scout.app import open_pdf_file
from pdf_scout.extract import (
    guess_body_spacing,
    raw_extract_words,
    add_line_spacing_to_words,
    guess_left_margin,
    extract_all_words,
)
from pdf_scout.tests.input_files import INPUT_FILES


def test_raw_extract_words(snapshot):
    for file_path in INPUT_FILES:
        file = open_pdf_file(file_path)
        output = raw_extract_words(file)
        snapshot.assert_match(output)


def test_guess_body_spacing(snapshot):
    for file_path in INPUT_FILES:
        file = open_pdf_file(file_path)
        all_words = raw_extract_words(file)
        all_words = add_line_spacing_to_words(file, all_words)
        body_spacing = guess_body_spacing(all_words)
        snapshot.assert_match(body_spacing)


def test_guess_left_margin(snapshot):
    for file_path in INPUT_FILES:
        file = open_pdf_file(file_path)
        all_words = raw_extract_words(file)
        left_margin = guess_left_margin(all_words)
        snapshot.assert_match(left_margin)


def test_extract_all_words(snapshot):
    for file_path in INPUT_FILES:
        file = open_pdf_file(file_path)
        all_words = extract_all_words(file)
        snapshot.assert_match(all_words)
