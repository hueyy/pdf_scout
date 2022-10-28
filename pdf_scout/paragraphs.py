from typing import List
from pdf_scout.types import Word
import math


def group_words_in_paragraphs(words: List[Word]) -> List[List[Word]]:
    groups: List[List[Word]] = []
    current_group: List[Word] = []
    line_spacing = 0

    for word in words:
        if len(current_group) == 0:
            current_group.append(word)
            line_spacing = word["bottom_spacing"]
        elif math.isclose(
            line_spacing, word["top"] - current_group[-1]["bottom"], rel_tol=0.01
        ) and math.isclose(line_spacing, word["bottom_spacing"], rel_tol=0.01):
            current_group.append(word)
        else:
            groups.append(current_group)
            current_group = [word]
            line_spacing = word["bottom_spacing"]
    groups.append(current_group)
    return groups
