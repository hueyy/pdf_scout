from pdf_scout.tests.input_files import INPUT_FILES
from pdf_scout.app import open_pdf_file
from pdf_scout.extract import raw_extract_words, extract_all_words
import pytest


@pytest.fixture(scope="session", params=INPUT_FILES)
def file_output(request):
    return open_pdf_file(request.param)


@pytest.fixture(scope="session")
def file_raw_output(file_output):
    file = file_output
    return file, raw_extract_words(file)


@pytest.fixture(scope="session")
def file_clean_output(file_output):
    file = file_output
    return file, extract_all_words(file)
