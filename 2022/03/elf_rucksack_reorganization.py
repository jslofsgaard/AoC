from typing import List, Union


class Rucksack:
    def __init__(self, left_compartment: str, right_compartment: str):
        if len(left_compartment) != len(right_compartment):
            raise ValueError

        self.left_compartment = left_compartment
        self.right_compartment = right_compartment

    @property
    def contents(self):
        return self.left_compartment + self.right_compartment

    @property
    def left_types(self):
        return set(self.left_compartment)

    @property
    def right_types(self):
        return set(self.right_compartment)

    @property
    def shared_types(self):
        return self.left_types & self.right_types

    @property
    def types(self):
        return self.left_types | self.right_types


class ElfGroup:
    def __init__(self, rucksacks):
        if len(rucksacks) != 3:
            raise ValueError('An elf group needs to have three Rustsacks!')

        self.rucksacks = rucksacks

    @property
    def badge(self):
        return (
            self.rucksacks[0].types &
            self.rucksacks[1].types &
            self.rucksacks[2].types
        ).pop()


def get_priority(item_type: str) -> int:
    lowercase_priorites = {
        'a': 1,
        'b': 2,
        'c': 3,
        'd': 4,
        'e': 5,
        'f': 6,
        'g': 7,
        'h': 8,
        'i': 9,
        'j': 10,
        'k': 11,
        'l': 12,
        'm': 13,
        'n': 14,
        'o': 15,
        'p': 16,
        'q': 17,
        'r': 18,
        's': 19,
        't': 20,
        'u': 21,
        'v': 22,
        'w': 23,
        'x': 24,
        'y': 25,
        'z': 26
    }
    if item_type.islower():
        return lowercase_priorites[item_type]
    else:
        return lowercase_priorites[item_type.lower()] + 26


def parse_line(line: str) -> Union[Rucksack, None]:
    """Return a rucksack constructed from the line if possible, None otherwise.
    """
    if line:
        middle = len(line) // 2
        return Rucksack(
            line[0:middle],
            line[middle:-1]
        )
    else:
        return None


def get_rucksacks(puzzle_input: str = 'input.txt') -> List[Rucksack]:
    """Construct a list of Rucksacks from the input located at puzzle_input.
    """
    with open(puzzle_input) as f:
        sacks = []
        rucksack = parse_line(f.readline())
        while rucksack:
            sacks.append(rucksack)
            rucksack = parse_line(f.readline())

        return sacks


def get_groups(rucksacks: List[Rucksack]) -> List[ElfGroup]:
    groups = []
    for i in range(len(rucksacks) // 3):
        groups.append(ElfGroup(rucksacks[i*3:i*3+3]))

    return groups


if __name__ == '__main__':
    rucksacks = get_rucksacks()
    groups = get_groups(rucksacks)
    total_duplicate_priority = sum(map(
        lambda rucksack: get_priority(rucksack.shared_types.pop()),
        rucksacks
    ))
    total_badge_priority = sum(map(
        lambda group: get_priority(group.badge),
        groups
    ))

    print(f'Total duplicate priority: {total_duplicate_priority}')
    print(f'Total badge priority: {total_badge_priority}')
