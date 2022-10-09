def test_score_words(scored_words_output, snapshot):
    _, output = scored_words_output
    snapshot.assert_match(output)
