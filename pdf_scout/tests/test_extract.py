from pdf_scout.extract import (
    guess_body_spacing,
    add_line_spacing_to_words,
    guess_left_margin,
)


def test_raw_extract_words(file_raw_output, snapshot):
    _, raw_extracted_words = file_raw_output
    snapshot.assert_match(raw_extracted_words)


def test_guess_body_spacing(file_raw_output, snapshot):
    file, raw_extracted_words = file_raw_output
    all_words_with_line_spacing = add_line_spacing_to_words(file, raw_extracted_words)
    body_spacing = guess_body_spacing(all_words_with_line_spacing)
    snapshot.assert_match(body_spacing)


def test_guess_left_margin(file_raw_output, snapshot):
    file, raw_extracted_words = file_raw_output
    left_margin = guess_left_margin(file, raw_extracted_words)
    snapshot.assert_match(left_margin)


def test_extract_all_words(file_clean_output, snapshot):
    _, all_words_tuple = file_clean_output
    snapshot.assert_match(all_words_tuple)
