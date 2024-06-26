import math
from collections import defaultdict
import itertools
from enum import Enum
from typing import Iterator, Iterable


Position = tuple[int, int]


class JetDirection(Enum):
    LEFT = "<"
    RIGHT = ">"


def parse_input(path="input.txt") -> list[JetDirection]:
    """A repeating iterator of jet directions with repating pattern at PATH."""

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
        self.nrocks = 0

    def __repr__(self) -> str:
        return f"Chamber({self.width})"

    def __str__(self) -> str:
        def select_char(x, y):
            if (x, y) in self:
                return "#"

            elif y in (-1, self.width) and x != -1:
                return "|"

            elif y in (-1, self.width) and x == -1:
                return "+"

            elif x == -1:
                return "-"

            return "."

        drawing = "\n".join([
            "".join([select_char(x, y) for y in range(-1, self.width + 1)])
            for x in reversed(range(-1, self.height + 2))
        ])
        return f"rocks: {self.nrocks}, width: {self.width}\n{drawing}"

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

            elif y in (-1, self.width) and x != -1:
                return "|"

            elif y in (-1, self.width) and x == -1:
                return "+"

            elif x == -1:
                return "-"

            return "."

        height = max(self.height, max([x for (x, _) in falling], default=0))
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
        self.nrocks += 1


class Simulation:
    """A simulation of rocks falling in a chamber."""

    def __init__(self, jets: Iterator[JetDirection], chamber_width: int = 7):
        self.chamber = Chamber(chamber_width)
        self.rocks = rocks()
        self.jets = jets
        self.jet_iterations = 0

    def _next_jet(self) -> JetDirection:
        self.jet_iterations += 1
        return next(self.jets)

    def _next_rock(self, max_jets: int = math.inf, do_print: bool = False) -> tuple[Rock, Position] | None:
        """Simulate a rock falling in the chamber.

        Adds the rock to the chamber if there are enough jet iterations left to determine
        where the rock will come to rest in the chamber. In which case, this method
        returns nothing. If there are not enought jet iterations left, the currently
        falling rock along with its position is returned.
        """
        rock = next(self.rocks)

        x0, y0 = self.chamber.starting_position()
        if do_print:
            print(f"Start {x0, y0} next rock:\n{self.draw((rock, (x0, y0)))}")

        x, y = self._move_rock(rock, self._next_jet(), (x0, y0), do_print)
        while x - x0 != 0:

            if self.jet_iterations >= max_jets:
                return rock, (x, y)

            x0, y0 = x, y
            x, y = self._move_rock(rock, self._next_jet(), (x0, y0), do_print)

        self.chamber.add_rock((x, y), rock)

    def _move_rock(self, rock: Rock, jet: JetDirection, current: Position, do_print: bool = False) -> Position:
        """ROCKs change in position having been moved by JET."""

        def apply_jet(x, y):
            """A rock can be shifted to the left or right by a jet of gas."""
            dy = -1 if jet == JetDirection.LEFT else 1
            next_positions = rock.positions(x, y + dy)
            if (
                    any(p in self.chamber for p in next_positions)
                    or any(y in (-1, self.chamber.width) for (_, y) in next_positions)
            ):
                result = x, y
            else:
                result = x, y + dy

            if do_print:
                print(f"Move jet {jet.name} {result}:\n{self.draw((rock, result))}")

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
                print(f"Move gravity {result}:\n{self.draw((rock, result))}")

            return result

        x0, y0 = current
        return apply_gravity(*apply_jet(x0, y0))

    def draw(self, falling: tuple[Rock, Position] | None = None) -> str:
        """Print the chamber, along with the falling ROCK at POSITION if any."""
        if not falling:
            return self.chamber.draw_falling()

        rock, position = falling
        return self.chamber.draw_falling(rock.positions(*position))

    def run(self, nrocks: int, do_print: bool = False) -> Chamber:
        """Run simulation untill NROCKS have been added."""
        for _ in range(nrocks):
            self._next_rock(do_print=do_print)

        return self.chamber

    def run2(self, njets: int, do_print: bool = False) -> tuple[Chamber, tuple[Rock, Position]]:
        """Run simulation untill NJETS have been consumed."""
        falling = None
        while self.jet_iterations < njets:
            falling = self._next_rock(njets, do_print=do_print)

        return self.chamber, falling


def simulation(path: str = "input.txt", width: int = 7) -> Simulation:
    return Simulation(cycle_jets(parse_input(path)), chamber_width=width)


def search_cycle(path: str = "input.txt", width: int = 7, do_print: bool = False) -> tuple[int, int, int] | None:
    """Search for a cyclical pattern in the falling rock created by input at PATH using a chamber of WIDTH."""
    njets = len(parse_input(path))
    max_cycle_length = njets * 100
    max_offset = njets * 100

    def dump_info(info: str):
        print(f"Cycle length: {cycle_length}, offset: {offset}, " + info)

    def cycle(chamber, cycle_length):
        return [
            chamber.rows[i] for i in range(max(chamber.height - cycle_length, 0), chamber.height)]

    for offset in range(0, max_offset):
        for cycle_length in range(5, max_cycle_length, 5):
            nrocks1 = offset + cycle_length
            nrocks2 = offset + cycle_length * 2
            nrocks3 = offset + cycle_length * 3

            if do_print:
                dump_info(f"rocks: ({nrocks1}, {nrocks2}, {nrocks3})")

            c1 = simulation(path, width).run(nrocks1)
            c2 = simulation(path, width).run(nrocks2)
            c3 = simulation(path, width).run(nrocks3)

            if (
                all(
                    cycle(a, cycle_length) == cycle(b, cycle_length)
                    for (a, b) in itertools.combinations((c1, c2, c3), 2)
                )
                and c3.height - c2.height == c2.height - c1.height
            ):
                if do_print:
                    dump_info(f"height diff: {c2.height - c1.height}")

                return offset, cycle_length, c2.height - c1.height

    print("No repeating sequence found!")


def draw_repeat(n: int, path: str = "input.txt", width: int = 7, offset: int = 0, cycle_length: int = 10) -> None:
    for i in range(1, n + 1):
        sim = simulation(path, width)
        chamber = sim.run(offset + cycle_length * i)
        drawing = sim.draw()
        filename = f"{path.split('.')[0]}-drawing-{i}-width-{width}.txt" 

        with open(filename, "w") as fp:
            fp.write("\n".join((
                f"input: {path}",
                f"width: {width}",
                f"offset: {offset}",
                f"cycle length: {cycle_length}",
                f"cycles: {i}",
                f"height: {chamber.height}",
                f"rocks: {chamber.nrocks}",
                f"drawing:\n"
            )))
            fp.write(drawing)


def debug_drawings(path: str = "input.txt"):
    for width in (7, 9, 10):
        repetition_pattern = search_cycle(path, width)
        if repetition_pattern is None:
            print(f"No repating pattern for width = {width}")
            continue

        offset, cycle_length, _ = repetition_pattern
        draw_repeat(5, path, width, offset, cycle_length)


def main(path: str = "input.txt"):
    # Part 1
    chamber = simulation(path).run(2022)
    print(f"The height of the rock tower after 2022 rocks have fallen is: {chamber.height}")

    # Part 2
    total_rocks = 1_000_000_000_000
    repetition_pattern = search_cycle(path)
    if repetition_pattern is None:
        print(f"Unable to determine height after {total_rocks} have fallen, no repeating pattern found!")
        return

    offset, cycle_length, dheight = repetition_pattern
    cycles = total_rocks // cycle_length
    one_cycle_height = simulation(path).run(offset + cycle_length + (total_rocks - cycle_length * cycles)).height

    print(
        f"The height of the rock tower after {total_rocks} have fallen is: {(cycles - 1) * dheight + one_cycle_height}"
    )


if __name__ == "__main__":
    main()
