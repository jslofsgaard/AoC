from collections import defaultdict
from enum import IntEnum
from functools import cached_property
from itertools import chain
from typing import DefaultDict, Iterable, Self

Coordinate = tuple[int, int]


def parse_input(path="input.txt") -> list["Path"]:
    paths = []
    with open(path, "r") as fp:
        line = fp.readline()
        while line:
            paths.append(
                Path([eval("(" + chars + ")") for chars in line.split(" -> ")])
            )
            line = fp.readline()

    return paths


class Path:
    def __init__(self, edges: Iterable[Coordinate]):
        self.edges = tuple(edges)

    def __repr__(self) -> None:
        return f"Path({self.edges})"

    @property
    def is_valid(self) -> bool:
        """A path is valid iff all its edges have a common row or column connecting them."""
        if any(
            start[0] != end[0] and start[1] != end[1]
            for start, end in zip(self.edges[:-1], self.edges[1:])
        ):
            return False

        return True

    @cached_property
    def coordinates(self) -> Iterable[Coordinate]:
        """All the coordinates connecting the edges of the path."""

        assert self.is_valid

        def expand(start: Coordinate, end: Coordinate) -> list[Coordinate]:
            """Expands a pair of coordinates into a list of coordinates covering every
            possible coordinate between and including the pair.

            """
            if start[0] != end[0]:
                return [
                    (i, start[1])
                    for i in range(min(start[0], end[0]), max(start[0], end[0]) + 1)
                ]
            else:
                return [
                    (start[0], i)
                    for i in range(min(start[1], end[1]), max(start[1], end[1]) + 1)
                ]

        return set(
            chain.from_iterable(
                expand(start, end)
                for start, end in zip(self.edges[:-1], self.edges[1:])
            )
        )


class Entity(IntEnum):
    air = 0
    rock = 1
    sand = 2
    source = 3


class CaveOutOfBoundsError(Exception):
    pass


class CaveCannotAddSandError(Exception):
    pass


class Cave:
    def __init__(
        self,
        source: Coordinate = (500, 0),
        rock_paths: Iterable[Path] = (),
        sand_coordinates: Iterable[Coordinate] = (),
        has_floor: bool = False,
        padding: int = 1,
    ):
        self.source_coordinate = source
        self.sand_coordinates = tuple(sand_coordinates)
        self.rock_paths = tuple(rock_paths)
        self.has_floor = has_floor
        self.padding = padding

    def __repr__(self) -> str:
        return (
            "Cave("
            + ",".join(
                (
                    f"source={self.source_coordinate},",
                    f"rock_paths={self.rock_paths},",
                    f"sand_coordinates={self.sand_coordinates},",
                    f"has_floor={self.has_floor}",
                    f"padding={self.padding},",
                )
            )
            + ")"
        )

    def __str__(self) -> None:
        # construct an array of cave entities
        source_x, source_y = self.source_coordinate
        min_x, max_x = self.x_range
        min_y, max_y = self.y_range

        ncol = max_x - min_x + 1
        nrow = max_y - min_y + 1

        array = [[Entity.air for _ in range(ncol)] for _ in range(nrow)]
        array[source_y - min_y][source_x - min_x] = Entity.source
        for x, y in self.rock_coordinates:
            array[y - min_y][x - min_x] = Entity.rock

        for x, y in self.sand_coordinates:
            array[y - min_y][x - min_x] = Entity.sand

        # add floor?
        if self.has_floor:
            if max_y == max(
                y for x, y in self.rock_coordinates
            ):  # nothing below lowest rock
                array.append([Entity.air for _ in range(ncol)])

            array.append([Entity.rock for _ in range(ncol)])

        # apply padding to it
        col_pad = [Entity.air for _ in range(self.padding)]
        row_pad = [
            col_pad + [Entity.air for _ in range(ncol)] + col_pad
            for _ in range(self.padding)
        ]
        array = row_pad + [col_pad + list(row) + col_pad for row in array] + row_pad

        # convert it to a /graphic/ string
        chars = {
            Entity.air: ".",
            Entity.rock: "#",
            Entity.sand: "o",
            Entity.source: "+",
        }

        return "\n".join("".join(chars[item] for item in row) for row in array)

    def __contains__(self, coordinate: Coordinate) -> bool:
        """A cave contains a pair of coordinates if they do not designate a position
        above its roof nor below its floor.

        """
        x, y = coordinate
        min_x, max_x = self.x_range
        min_y, max_y = self.y_range
        if not self.has_floor:
            return min_y <= y
        else:
            return min_y <= y <= self.floor_level

    def __getitem__(self, coordinate: Coordinate) -> Entity:
        x, y = coordinate
        if (x, y) not in self:
            raise CaveOutOfBoundsError()

        if y == self.floor_level:
            return Entity.rock

        return self.grid[x, y]

    @cached_property
    def rock_coordinates(self) -> tuple[Coordinate]:
        return tuple(chain.from_iterable(path.coordinates for path in self.rock_paths))

    @cached_property
    def x_range(self) -> tuple[Coordinate]:
        """The horisontal range of coordinates in which there is something besides air."""
        crds = (
            list(self.rock_coordinates)
            + [self.source_coordinate]
            + list(self.sand_coordinates)
        )
        return min(x for x, y in crds), max(x for x, y in crds)

    @cached_property
    def y_range(self) -> tuple[Coordinate]:
        """The vertical range of coordinates in which there is something besides air."""
        crds = (
            list(self.rock_coordinates)
            + [self.source_coordinate]
            + list(self.sand_coordinates)
        )
        return min(y for x, y in crds), max(y for x, y in crds)

    @cached_property
    def floor_level(self) -> int | None:
        if not self.has_floor:
            return None

        return max(y for x, y in self.rock_coordinates) + 2

    @cached_property
    def grid(self) -> DefaultDict[Coordinate, Entity]:
        grid = defaultdict(lambda: Entity.air)
        grid[self.source_coordinate] = Entity.source
        for x, y in self.rock_coordinates:
            grid[x, y] = Entity.rock

        for x, y in self.sand_coordinates:
            grid[x, y] = Entity.sand

        return grid

    @cached_property
    def nrock(self) -> int:
        return len(self.rock_coordinates)

    @cached_property
    def nsand(self) -> int:
        return len(self.sand_coordinates)

    def simulate(self) -> Coordinate | None:
        """Simulate a grain of sand falling from the source, return
        the coordinates it will land on.

        If the cave has no floor and the grain will continue to fall forever, return
        None.

        If it does have a floor, this method will always return a coordinate. Eventually
        returning the coordinate of the source once the cave is filled with sand.

        """
        _, max_y = self.y_range

        def step(x, y) -> Coordinate | None:
            # fallen off?
            if not self.has_floor and max_y < y:
                return None

            # down one step
            if self[x, y + 1] == Entity.air:
                return step(x, y + 1)

            # down and to the left
            if self[x - 1, y + 1] == Entity.air:
                return step(x - 1, y + 1)

            # down and to the right
            if self[x + 1, y + 1] == Entity.air:
                return step(x + 1, y + 1)

            return x, y

        return step(*self.source_coordinate)

    def add_sand(self, x: int, y: int) -> Self:
        """Create a new cave with a sand added to the designated position."""
        if (x, y) not in self:
            raise CaveOutOfBoundsError()

        if self[x, y] in (Entity.rock, Entity.sand):
            raise CaveCannotAddSandError(
                f"cannot add sand to a position already occupied by a {self[x, y].name}"
            )

        return Cave(
            self.source_coordinate,
            self.rock_paths,
            list(self.sand_coordinates) + [(x, y)],
            self.has_floor,
            self.padding,
        )

    def add_floor(self) -> Self:
        return Cave(
            self.source_coordinate,
            self.rock_paths,
            self.sand_coordinates,
            True,
            self.padding,
        )


if __name__ == "__main__":
    # Part 1
    cave = Cave(rock_paths=parse_input())
    crd = cave.simulate()
    while crd is not None:
        cave = cave.add_sand(*crd)
        crd = cave.simulate()

    print(cave)
    print(f"Grains of sand in floor less cave: {cave.nsand}")

    # Part 2
    cave = cave.add_floor()
    crd = cave.simulate()
    while crd != cave.source_coordinate:
        cave = cave.add_sand(*crd)
        crd = cave.simulate()

    cave = cave.add_sand(*cave.source_coordinate)
    print(cave)
    print(f"Grains of sand in floored cave: {cave.nsand}")
