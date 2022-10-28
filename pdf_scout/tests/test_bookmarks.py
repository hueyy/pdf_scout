from pdf_scout.bookmarks import generate_bookmarks
from pdf_scout.app import get_top_scored_paragraphs


def test_generate_bookmarks(scored_words_output, snapshot):
    file, scored_words = scored_words_output
    top_scored_words = get_top_scored_paragraphs(scored_words, 3)
    bookmarks = generate_bookmarks(file, top_scored_words)
    snapshot.assert_match(bookmarks)
