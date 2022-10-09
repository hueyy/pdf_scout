from pdf_scout.tests.input_files import INPUT_FILES
from pdf_scout.extract import raw_extract_words, extract_all_words
from pdf_scout.scoring import score_words
import pytest
import pdfplumber
from operator import itemgetter
from typing import Tuple, List
from pdf_scout.types import DocumentWords, HeadingScore, RawWord, Word


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
def file_clean_output(
    file_output: pdfplumber.PDF,
) -> Tuple[pdfplumber.PDF, DocumentWords]:
    file = file_output
    return file, extract_all_words(file)


@pytest.fixture(scope="session")
def scored_words_output(
    file_clean_output: Tuple[pdfplumber.PDF, DocumentWords]
) -> Tuple[pdfplumber.PDF, List[Tuple[HeadingScore, Word]]]:
    file, extracted_words = file_clean_output
    all_words, non_body_words = itemgetter("all_words", "non_body_words")(
        extracted_words
    )
    scored_words = score_words(all_words, non_body_words)
    return file, scored_words
