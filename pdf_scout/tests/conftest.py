from pdf_scout.tests.input_files import INPUT_FILES
from pdf_scout.extract import raw_extract_words, extract_all_lines, words_to_lines
from pdf_scout.paragraphs import group_lines_in_paragraphs
from pdf_scout.scoring import score_paragraphs
import pytest
import pdfplumber
from operator import itemgetter
from typing import Tuple, List
from pdf_scout.custom_types import DocumentLines, HeadingScore, RawWord, Word


@pytest.fixture(scope="session", params=INPUT_FILES)
def file_output(request) -> pdfplumber.PDF:
    return pdfplumber.open(request.param)


@pytest.fixture(scope="session")
def file_raw_output(
    file_output: pdfplumber.PDF,
) -> Tuple[pdfplumber.PDF, List[RawWord]]:
    file = file_output
    return file, raw_extract_words(file)


@pytest.fixture(scope="session")
def file_lines_output(
    file_raw_output: Tuple[pdfplumber.PDF, List[RawWord]],
) -> Tuple[pdfplumber.PDF, List[List[RawWord]]]:
    file, raw_words = file_raw_output
    return file, words_to_lines(raw_words)


@pytest.fixture(scope="session")
def file_clean_output(
    file_output: pdfplumber.PDF,
) -> Tuple[pdfplumber.PDF, DocumentLines]:
    file = file_output
    return file, extract_all_lines(file)


@pytest.fixture(scope="session")
def paragraphs_output(
    file_clean_output: Tuple[pdfplumber.PDF, DocumentLines]
) -> Tuple[pdfplumber.PDF, List[List[Word]], List[List[List[Word]]]]:
    file, extracted_lines = file_clean_output
    all_lines, heading_lines = itemgetter("all_lines", "heading_lines")(extracted_lines)
    heading_paragraphs = group_lines_in_paragraphs(heading_lines)
    return file, all_lines, heading_paragraphs


@pytest.fixture(scope="session")
def scored_words_output(
    paragraphs_output,
) -> Tuple[pdfplumber.PDF, List[Tuple[HeadingScore, List[List[Word]]]]]:
    file, all_words, heading_paragraphs = paragraphs_output
    scored_paragraphs = score_paragraphs(all_words, heading_paragraphs)
    return file, scored_paragraphs
