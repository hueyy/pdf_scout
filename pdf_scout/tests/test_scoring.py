from pdf_scout.scoring import score_words


def test_score_words(file_clean_output, snapshot):
    _, extracted_words = file_clean_output
    all_words, non_body_words = extracted_words
    scored_words = score_words(all_words, non_body_words)
    snapshot.assert_match(scored_words)
