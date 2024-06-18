from collections import defaultdict
from functools import cache
from itertools import product
import itertools
from enum import Enum
from typing import Iterator, Iterable


Position = tuple[int, int]

class JetDirection(Enum):
    LEFT = "<"
    RIGHT = ">"


def parse_input(path="input.txt") -> list[JetDirection]:
    """An repeating iterator of jet directions with repating pattern at PATH."""

    def jet(char) -> JetDirection:
        return {
            ">": JetDirection.RIGHT,
            "<": JetDirection.LEFT
        }[char]

    with open(path, "r") as fp:
        chars = fp.readline().strip()

    return [jet(direction) for direction in chars]


def cycle_jets(directions: list[JetDirection]) -> Iterator[JetDirection]:
    for direction in itertools.cycle(directions):
        yield direction


def coordinates(drawing: list[str]) -> set[Position]:
    """The coordinates of ASCII rock drawing relative to the bottom left corner."""

    width = max(len(row) for row in drawing)
    height = len(drawing)

    def search():
        for row in range(height):
            for col in range(width):
                if drawing[row][col] == "#":
                    yield height - 1 - row, col

    return set(search())


class RockShape(Enum):
    HLINE = coordinates(["####"])
    CROSS = coordinates([
        ".#.",
        "###",
        ".#.",
    ])
    ELL = coordinates([
        "..#",
        "..#",
        "###"
    ])
    VLINE = coordinates([
        "#",
        "#",
        "#",
        "#",
    ])
    SQUARE = coordinates([
        "##",
        "##",
    ])


class Rock:
    "An origin (bottom left) and a list of positions relative to the origin (the shape)."

    def __init__(self, shape: RockShape):
        self.shape = shape

    def __repr__(self) -> str:
        return f"Rock({self.shape})"

    def __str__(self) -> str:
        drawing = "\n".join([
            "".join([("#" if (x, y) in self.shape.value else ".") for y in range(self.width)])
            for x in reversed(range(self.height))
        ])
        return f"name: {self.shape.name}, width: {self.width}, height: {self.height}\n{self.shape.value}\n{drawing}"

    @property
    def height(self) -> int:
        "The number of rows in the rock's shape."

        return max(x for x, y in self.shape.value) + 1

    @property
    def width(self) -> int:
        "The number of columns in the rock's shape."

        return max(y for x, y in self.shape.value) + 1

    def positions(self, x, y) -> set[Position]:
        "All the points occupied by the rock relative (bottom left) to x, y."

        return set(
            ((x + dx, y + dy) for (dx, dy) in self.shape.value)
        )


def rocks():
    "A repating iterator of ROCK objects yielding them in the order they fall in the cave."

    for shape in itertools.cycle(RockShape):
        yield Rock(shape)


class Chamber:
    "A collection of non-overlapping (not enforced) ROCKs."

    def __init__(self, width: int = 7):
        self.width = width
        self.height = 0
        self.rows = defaultdict(set)

    def __repr__(self) -> str:
        return f"Chamber({self.width})"

    def __str__(self) -> str:
        def select_char(x, y):
            if (x, y) in self:
                return "#"

            elif y in (-1, 7) and x != -1:
                return "|"

            elif y in (-1, 7) and x == -1:
                return "+"

            elif x == -1:
                return "-"

            return "."

        drawing = "\n".join([
            "".join([select_char(x, y) for y in range(-1, self.width + 1)])
            for x in reversed(range(-1, self.height + 2))
        ])
        return f"total: {len(self.rows)}, width: {self.width}\n{drawing}"

    def __contains__(self, position: Position) -> bool:
        x, y = position
        return x in self.rows and y in self.rows[x]

    def draw_falling(self, falling: Iterable[Position] = ()):
        falling = list(falling)

        def select_char(x, y):
            if (x, y) in self:
                return "#"

            elif (x, y) in falling:
                return "@"

            elif y in (-1, 7) and x != -1:
                return "|"

            elif y in (-1, 7) and x == -1:
                return "+"

            elif x == -1:
                return "-"

            return "."

        height = max(self.height, *[x for (x, _) in falling])
        drawing = "\n".join([
            "".join([select_char(x, y) for y in range(-1, self.width + 1)])
            for x in reversed(range(-1, height + 2))
        ])
        return drawing
        
    def starting_position(self) -> Position:
        """The next position where a rock will appear."""

        return 3 + self.height, 2

    def add_rock(self, position: Position, rock: Rock) -> None:
        """Add a ROCK to the chamber with its origin at POSITION."""

        x0, y0 = position
        positions = rock.positions(x0, y0)
        for x, y in positions:
            self.rows[x].add(y)

        self.height = max(self.height, *[x + 1 for (x,y) in positions])


class Simulation:
    """A simulation of rocks falling in a chamber."""

    def __init__(self, jets: Iterator[JetDirection], chamber_width: int = 7):
        self.chamber = Chamber(chamber_width)
        self.rocks = rocks()
        self.jets = jets

    def _next_rock(self, do_print: bool = False) -> None:
        """Simulate a rock falling in the chamber.

        Adds a rock to the chamber determining where it will come to
        rest as it falls down from the current starting position of
        the chamber blown by the next sequence of jets.
        """
        rock = next(self.rocks)

        x0, y0 = self.chamber.starting_position()
        if do_print:
            print(f"Start {x0, y0} next rock:\n{self.draw(rock, (x0, y0))}")

        x, y = self._move_rock(rock, next(self.jets), (x0, y0), do_print)
        while x - x0 != 0:
            x0, y0 = x, y
            x, y = self._move_rock(rock, next(self.jets), (x0, y0), do_print)

        self.chamber.add_rock((x, y), rock)

    def _move_rock(self, rock: Rock, jet: JetDirection, current: Position, do_print: bool = False) -> Position:
        """ROCKs change in position having been moved by JET."""

        def apply_jet(x, y):
            """A rock can be shifted to the left or right by a jet of gas."""
            dy = -1 if jet == JetDirection.LEFT else 1
            next_positions = rock.positions(x, y + dy)
            if any(p in self.chamber for p in next_positions) or any(y in (-1, 7) for (_, y) in next_positions):
                result = x, y
            else:
                result = x, y + dy

            if do_print:
                print(f"Move jet {jet.name} {result}:\n{self.draw(rock, result)}")

            return result

        def apply_gravity(x, y):
            """A rock can be shifted downwards by gravity."""
            dx = - 1
            next_positions = rock.positions(x + dx, y)
            if any(p in self.chamber for p in next_positions) or any(x == -1 for (x, _) in next_positions):
                result = x, y
            else:
                result = x + dx, y

            if do_print:
                print(f"Move gravity {result}:\n{self.draw(rock, result)}")

            return result

        x0, y0 = current
        return apply_gravity(*apply_jet(x0, y0))

    def draw(self, rock: Rock = None, position: Position = None) -> str:
        """Print the chamber, along with the falling ROCK at POSITION if any."""
        if not rock or not position:
            return self.chamber.draw_falling()

        return self.chamber.draw_falling(rock.positions(*position))

    def run(self, nrocks: int, do_print: bool = False) -> Chamber:
        """Run simulation untill NROCKS have been added."""
        for _ in range(nrocks):
            self._next_rock(do_print)

        return self.chamber

    def search_plateau(self) -> Chamber:
        """Run simulation untill a plateau manifests."""
        i = 0
        self._next_rock()
        while all([len(row) != 7 for row in self.chamber.rows.values()]):
            self._next_rock()
            i += 1

        return i, self.chamber

def simulate(n: int, path: str = "input.txt"):
    simulation = Simulation(cycle_jets(parse_input(path)))
    chamber = simulation.run(n)
    print(f"The height of the tower after {n} rocks have stopped is: {chamber.height}")


if __name__ == "__main__":
    # Part 1
    simulate(2022)
