from pdf_scout.app import open_pdf_file
from pdf_scout.extract import extract_all_words
from pdf_scout.scoring import score_words
from pdf_scout.tests.input_files import INPUT_FILES


def test_score_words(snapshot):
    for file_path in INPUT_FILES:
        file = open_pdf_file(file_path)
        all_words, non_body_words = extract_all_words(file)
        scored_words = score_words(all_words, non_body_words)
        snapshot.assert_match(scored_words)
