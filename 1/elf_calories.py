from typing import Union, List


def parse_line(line: str) -> Union[int, None]:
    """Read a line and return an integer if the line can be converted
    to it, None otherwise.
    """
    try:
        return int(line)
    except ValueError:
        return None


class Elf:
    def __init__(self, aoc_input):
        self.set_calories(aoc_input)

    def set_calories(self, aoc_input):
        self.calories = []

        calorie = parse_line(aoc_input.readline())
        while calorie:
            self.calories.append(calorie)
            calorie = parse_line(aoc_input.readline())

    def get_total_calories(self):
        return sum(self.calories)


class ElfBand:
    def __init__(self):
        self.build_from_input()

    def build_from_input(self, aoc_input: str = 'input') -> List[Elf]:
        """Read the input and construct list of Elfs."""
        with open(aoc_input) as f:
            self.band = []
            elf = Elf(f)
            while elf.calories:
                self.band.append(elf)
                elf = Elf(f)

    def get_max_elf(self) -> Union[Elf, None]:
        """Returns the Elf with the highest calorie count, None if no
        elfs are to be found.
        """
        if self.band:
            max = 0
            for elf in self.band:
                if elf.get_total_calories() > max:
                    max = elf.get_total_calories()
                    max_elf = elf
            return max_elf
        else:
            return None

    def sort_elfs(self):
        """Sort the group of Elfs based on calorie carried."""
        self.band.sort(
            key=lambda elf: elf.get_total_calories(),
            reverse=True
        )


if __name__ == '__main__':
    elfs = ElfBand()
    elfs.sort_elfs()
    max_calories = elfs.band[0].get_total_calories()
    top_three_total = sum(
        map(
            lambda elf: elf.get_total_calories(),
            elfs.band[0:3]
        )
    )

    print(f'Max: {max_calories}')
    print(
        'Top three: '
        f'{elfs.band[0].get_total_calories()}, '
        f'{elfs.band[1].get_total_calories()}, '
        f'{elfs.band[2].get_total_calories()}'
    )
    print(f'Top three total: {top_three_total}')
