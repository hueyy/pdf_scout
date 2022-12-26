from typing import List
from pdf_scout.custom_types import Word
import math


def group_words_in_paragraphs(words: List[Word]) -> List[List[Word]]:
    groups: List[List[Word]] = []
    current_group: List[Word] = []
    paragraph_line_spacing = 0
    spacing_margin = 0.01

    for word in words:
        if len(current_group) == 0:
            current_group.append(word)
            paragraph_line_spacing = word["bottom_spacing"]
        elif (
            # assume spacing between lines in same paragraphs is less or equal to double line
            # spacing
            paragraph_line_spacing <= current_group[0]["size"] * 2 and
            math.isclose(
                # paragraph line_spacing is essentially the same as space between
                # previous member of group and current word
                paragraph_line_spacing, word["top_spacing"], rel_tol=spacing_margin
            ) and not (
                # the words should be considered separate paragraphs
                math.isclose(current_group[0]["top_spacing"], word["top_spacing"],  rel_tol=spacing_margin)
            )
        ):
            current_group.append(word)
        else:
            groups.append(current_group)
            current_group = [word]
            paragraph_line_spacing = word["bottom_spacing"]
    groups.append(current_group)
    return groups
