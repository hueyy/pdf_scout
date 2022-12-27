from typing import List
from pdf_scout.custom_types import Word
import math

SPACING_MARGIN = 0.01


def has_reasonable_paragraph_line_spacing(
    paragraph_line_spacing: float, current_group: List[List[Word]]
) -> bool:
    # assume spacing between lines in same paragraphs is less or equal to double line
    # spacing
    return paragraph_line_spacing <= current_group[0][0]["size"] * 1.2


def are_consecutive_lines(
    paragraph_line_spacing: float, line: List[Word], current_group: List[List[Word]]
) -> bool:
    # this is necessary to handle cases where the words are separated
    # by body text
    return math.isclose(
        paragraph_line_spacing,
        line[0]["top"] - current_group[-1][0]["bottom"],
        rel_tol=SPACING_MARGIN,
    ) and math.isclose(
        # paragraph line_spacing is essentially the same as space between
        # previous member of group and current word
        paragraph_line_spacing,
        line[0]["top_spacing"],
        rel_tol=SPACING_MARGIN,
    )


def are_separate_paragraphs(
    line: List[Word],
    current_group: List[List[Word]],
) -> bool:
    # the words should be considered separate paragraphs
    return math.isclose(
        current_group[0][0]["top_spacing"],
        line[0]["top_spacing"],
        rel_tol=SPACING_MARGIN,
    )


def group_lines_in_paragraphs(lines: List[List[Word]]) -> List[List[List[Word]]]:
    groups: List[List[List[Word]]] = []
    current_group: List[List[Word]] = []
    paragraph_line_spacing: float = 0

    for line in lines:
        if len(current_group) == 0:
            current_group.append(line)
            paragraph_line_spacing = line[0]["bottom_spacing"]
        elif (
            has_reasonable_paragraph_line_spacing(paragraph_line_spacing, current_group)
            and
            # # top line is longer than bottom line
            # math.isclose(
            #     current_group[-1]["x1"] - word["x1"], 0, rel_tol=0.01
            # ) and
            are_consecutive_lines(paragraph_line_spacing, line, current_group)
            and not are_separate_paragraphs(line, current_group)
        ):
            current_group.append(line)
        else:
            groups.append(current_group)
            current_group = [line]
            paragraph_line_spacing = line[0]["bottom_spacing"]
    groups.append(current_group)
    return groups
