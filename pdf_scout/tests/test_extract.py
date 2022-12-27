from pdf_scout.extract import (
    guess_body_spacing,
    add_line_spacing_to_lines,
    guess_left_margin,
)
from typing import Tuple, List
from pdf_scout.custom_types import DocumentLines, HeadingScore, RawWord, Word
import pdfplumber


def test_raw_extract_words(
    file_raw_output: Tuple[pdfplumber.PDF, List[RawWord]], snapshot
):
    _, raw_extracted_words = file_raw_output
    snapshot.assert_match(raw_extracted_words)


def test_guess_body_spacing(
    file_lines_output: Tuple[pdfplumber.PDF, List[List[RawWord]]], snapshot
):
    file, lines = file_lines_output
    all_lines_with_line_spacing = add_line_spacing_to_lines(file, lines)
    body_spacing: float = guess_body_spacing(all_lines_with_line_spacing)
    snapshot.assert_match(body_spacing)


def test_guess_left_margin(
    file_lines_output: Tuple[pdfplumber.PDF, List[List[RawWord]]], snapshot
):
    file, lines = file_lines_output
    all_lines_with_line_spacing = add_line_spacing_to_lines(file, lines)
    left_margin: List[float] = guess_left_margin(file, all_lines_with_line_spacing)
    snapshot.assert_match(left_margin)


def test_extract_all_words(file_clean_output, snapshot):
    _, all_words_tuple = file_clean_output
    snapshot.assert_match(all_words_tuple)
