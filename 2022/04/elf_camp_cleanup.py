from typing import List, Union


class Section:
    def __init__(self, start: int, stop: int):
        self.start = start
        self.stop = stop

    def contains(self, other) -> bool:
        if self.start <= other.start and other.stop <= self.stop:
            return True
        else:
            return False

    def overlaps(self, other) -> bool:
        if (  # There should be a better way to do this
            other.start <= self.start <= other.stop
            or other.start <= self.stop <= other.stop
            or self.start <= other.start <= self.stop
            or self.start <= other.stop <= self.stop
        ):
            return True

    def __str__(self):
        return f"{self.start} - {self.stop}"


class ElfPairing:
    def __init__(self, left_section: Section, right_section: Section):
        self.left_section = left_section
        self.right_section = right_section

    @property
    def containing_section(self) -> Union[Section, None]:
        """Is the section which contains the other, if one of them does contain
        the other, None otherwise.
        """
        if self.left_section.contains(self.right_section):
            return self.left_section
        elif self.right_section.contains(self.left_section):
            return self.right_section
        else:
            return None

    @property
    def overlap(self) -> bool:
        """Is true if the paring's sections overlap, false otherwise."""
        return self.left_section.overlaps(self.right_section)

    def __str__(self):
        return "Left: " + str(self.left_section) + ", Right: " + str(self.right_section)


def parse_line(line: str) -> Union[ElfPairing, None]:
    """Return an elf pairing constructed from the line if possible,
    None otherwise.
    """
    if line:
        sides = line.split(",")
        left = sides[0].split("-")
        right = sides[1].split("-")
        return ElfPairing(
            Section(int(left[0]), int(left[1])),
            Section(int(right[0]), int(right[1])),
        )
    else:
        return None


def get_pairings(puzzle_input: str = "input.txt") -> List[ElfPairing]:
    """Construct a list of elf pairings from the input located at puzzle_input."""
    with open(puzzle_input) as f:
        pairings = []
        pairing = parse_line(f.readline())
        while pairing:
            pairings.append(pairing)
            pairing = parse_line(f.readline())

        return pairings


if __name__ == "__main__":
    pairings = get_pairings()
    count_fully_contained = sum(
        map(lambda pairing: 1 if pairing.containing_section else 0, pairings)
    )
    count_overlaps = sum(map(lambda pairing: 1 if pairing.overlap else 0, pairings))

    print(f"Pairings with fully contained sections: {count_fully_contained}")
    print(f"Pairings with overlaping sections: {count_overlaps}")
