def test_group_words_in_paragraphs(paragraphs_output, snapshot):
  _, __, heading_paragraphs = paragraphs_output
  snapshot.assert_match(heading_paragraphs)