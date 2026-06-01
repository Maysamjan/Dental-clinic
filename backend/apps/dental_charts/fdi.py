"""FDI two-digit tooth numbering helpers.

Adult (permanent) quadrants 1-4, teeth 1-8  -> 11..18, 21..28, 31..38, 41..48
Child (primary)   quadrants 5-8, teeth 1-5  -> 51..55, 61..65, 71..75, 81..85
"""

TOOTH_NAMES = {
    1: "Central Incisor", 2: "Lateral Incisor", 3: "Canine",
    4: "First Premolar", 5: "Second Premolar",
    6: "First Molar", 7: "Second Molar", 8: "Third Molar",
}


def adult_teeth():
    teeth = []
    for quadrant in (1, 2, 3, 4):
        for pos in range(1, 9):
            teeth.append((quadrant * 10 + pos, TOOTH_NAMES[pos]))
    return teeth


def child_teeth():
    teeth = []
    for quadrant in (5, 6, 7, 8):
        for pos in range(1, 6):
            teeth.append((quadrant * 10 + pos, TOOTH_NAMES[pos]))
    return teeth


def teeth_for(dentition):
    return adult_teeth() if dentition == "ADULT" else child_teeth()
