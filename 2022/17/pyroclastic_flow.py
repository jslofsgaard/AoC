from functools import cache
import itertools
from enum import Enum
from typing import Iterator


class JetDirection(Enum):
    LEFT = "<"
    RIGHT = ">"


def parse_input(path="input.txt") -> Iterator[JetDirection]:

    def jet(char) -> JetDirection:
        return {
            ">": JetDirection.RIGHT,
            "<": JetDirection.LEFT
        }[char]

    with open(path, "r") as fp:
        chars = fp.readline().strip()

    for direction in itertools.cycle(chars):
        yield jet(direction)


class RockShape(Enum):
    HLINE = (
        (0,0),
        (1,0),
        (2,0),
        (3,0)
    )
    CROSS = (
        (1,0),
        (0,1),
        (1,1),
        (2,1),
        (1,2)
    )
    ELL = (
        (0,0),
        (1,0),
        (2,0),
        (2,1),
        (2,2)
    )
    VLINE = (
        (0,0),
        (0,1),
        (0,2),
        (0,3)
    )
    SQUARE = (
        (0,0),
        (1,0),
        (0,1),
        (1,1)
    )


class Rock:
    "A rock is just an origin and a list of positions relative to the origin (the shape)."
    def __init__(self, shape: RockShape, x = 0, y = 0):
        self.origin = x, y
        self.shape = shape

    def __repr__(self) -> str:
        x, y = self.origin
        return f"Rock({self.shape}, x={x}, y={y})"

    def __str__(self) -> str:
        return "\n".join([
            "".join([("#" if (x, y) in self.shape.value else ".") for x in range(self.width)])
            for y in reversed(range(self.height))
        ])

    @property
    def height(self) -> int:
        "The number of vertical points in the rock's shape."
        return max(
            y for x, y in self.shape.value
        ) + 1

    @property
    def width(self) -> int:
        "The number of horizontal points in the rock's shape."
        return max(
            x for x, y in self.shape.value
        ) + 1

    @property
    def positions(self) -> tuple[tuple[int, int]]:
        "All the points occupied by the rock"
        x, y = self.origin
        return tuple(
            ((x + dx, y + dy) for (dx, dy) in self.shape.value)
        )

def rocks():
    for shape in itertools.cycle(RockShape):
        yield Rock(shape)


class Chamber:
    def __init__(self, rocks: Iterator[Rock], jets: Iterator[JetDirection], width: int = 7):
        self.width = width
        self.rocks = rocks
        self.jets = jets
        self.at_rest = []

    def __repr__(self) -> str:
        return f"Chamber({self.rocks}, {self.jets}, {self.width})"

    def __str__(self) -> str:
        return "\n".join([
            "".join([("#" if (x, y) in self.positions else ".") for x in range(self.width)])
            for y in reversed(range(self.highest_point + 2))
        ])

    @property
    def positions(self) -> tuple[tuple[int,int]]:
        return tuple(itertools.chain.from_iterable(rock.positions for rock in self.at_rest))

    @property
    def no_overlap(self) -> bool:
        return len(set(self.positions)) == len(self.positions)

    @property
    def highest_point(self) -> int:
        return max((y + 1 for _, y in self.positions), default=0)

    def starting_position(self) -> tuple[int, int]:
        """The next position where a rock would appear."""
        return 2, 3 + self.highest_point

    def add_rock(self) -> None:
        rock = next(self.rocks)
        rock.origin = self.starting_position()

        def apply_jet() -> bool:
            """A rock can be shifted to the left or right by a jet of gas."""
            jet = next(self.jets)
            dx = -1 if jet == JetDirection.LEFT else 1
            next_positions = tuple((x + dx, y) for x, y in rock.positions)
            if (
                    any(pos in self.positions for pos in next_positions)
                    or min(x for x, _ in next_positions) < 0
                    or max(x for x, _ in next_positions) >= self.width
            ):
                return False

            x, y = rock.origin
            rock.origin = x + dx, y
            return True

        def apply_gravity() -> True:
            """A rock can be shifted downwards by gravity."""
            dy = - 1
            next_positions = tuple((x, y + dy) for x, y in rock.positions)
            if (
                    any(pos in self.positions for pos in next_positions)
                    or min(y for _, y in next_positions) < 0
            ):
                return False

            x, y = rock.origin
            rock.origin = x, y + dy
            return True

        apply_jet()
        while apply_gravity():
            apply_jet()
                
        self.at_rest.append(rock)


def simulate(nrocks: int) -> Chamber:
    chamber = Chamber(rocks(), parse_input())
    for _ in range(nrocks):
        chamber.add_rock()

    return chamber

if __name__ == "__main__":
    # Part 1
    chamber = simulate(2022)
    print(f"The height of the tower after 2022 rocks have stopped is: {chamber.highest_point}")
