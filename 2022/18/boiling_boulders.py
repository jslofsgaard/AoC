from typing import Iterable, Iterator
import itertools
import math

Point = tuple[int, int, int]
Side = Iterable[Point]


class Cube:

    def __init__(self, x: int, y: int, z: int, dx: int = 1, dy: int = 1, dz: int =  1):
        """Make a cube rooted at (X, Y, Z) with length DX, height DY and depth DZ."""
        self.origin = x, y, z
        self.lengths = dx, dy, dz

    def __eq__(self, other) -> bool:
        return self.origin == other.origin

    def __contains__(self, side: Side) -> bool:
        return side in self.sides

    @property
    def edges(self) -> set[Point]:
        x, y, z = self.origin
        dx, dy, dz = self.lengths
        return set((
            (x, y, z),
            (x, y, z + dz),
            (x, y + dy, z),
            (x, y + dy, z + dz),
            (x + dx, y, cubez),
            (x + dx, y, z + dz),
            (x + dx, y + dy, z),
            (x + dx, y + dy, z + dz),
        ))

    @property
    def sides(self) -> tuple[Side]:
        x, y, z = self.origin
        dx, dy, dz = self.lengths
        return (
            # Face (z constant)
            set((
                (x, y, z),
                (x, y + dy, z),
                (x + dx, y, z),
                (x + dx, y + dy, z),
            )),
            # Backface (z + dz constant)
            set((
                (x, y, z + dz),
                (x, y + dy, z + dz),
                (x + dx, y, z + dz),
                (x + dx, y + dy, z + dz),
            )),
            # Left side (x constant)
            set((
                (x, y, z),
                (x, y, z + dz),
                (x, y + dy, z),
                (x, y + dy, z + dz),
            )),
            # Right side (x + dz constant)
            set((
                (x + dx, y, z),
                (x + dx, y, z + dz),
                (x + dx, y + dy, z),
                (x + dx, y + dy, z + dz),
            )),
            # Bottom (y constant)
            set((
                (x, y, z),
                (x, y, z + dz),
                (x + dx, y, z),
                (x + dx, y, z + dz),
            )),
            # Top (y + dy constant)
            set((
                (x, y + dy, z),
                (x, y + dy, z + dz),
                (x + dx, y + dy, z),
                (x + dx, y + dy, z + dz),
            ))
        )


class CubeCollection:

    def __init__(self, cubes: list[Cube]):
        self.cubes = cubes

    def __contains__(self, cube: Cube) -> bool:
        for _cube in self.cubes:
            if cube == _cube:
                return True

        return False

    def sides(self) -> Iterator[Side]:
        for cube in self.cubes:
            for side in cube.sides:
                yield side

    def side_count(self) -> dict[Side: int]:
        sides = list(self.sides())
        return {tuple(side): sides.count(side) for side in sides}

    def free_surface_area(self) -> int:
        return sum([
            1 for side, count in self.side_count().items()
            if count == 1
        ])

    def exterior_surface_area(self) -> int:
        return len(self.contour())

    def axies(self) -> tuple[set[int], set[int], set[int]]:
        """All the points in the collection's sides split into three sets per axis."""

        X, Y, Z = set(), set(), set()
        for side in self.sides():
            for x, y, z in side:
                X.add(x)
                Y.add(y)
                Z.add(z)

        return X, Y, Z

    def contour(self) -> list[Side]:
        """The sides defining the contour of the cube collection."""

        X, Y, Z = self.axies()
        origin = min(X) - 1, min(Y) - 1, min(Z) - 1
        collection_origins = [cube.origin for cube in self.cubes]
        enclosing_cubes = [
            Cube(x, y, z) for x, y, z in itertools.product(
                range(min(X) - 1, max(X) + 1), range(min(Y) - 1, max(Y) + 1), range(min(Z) - 1, max(Z) + 1)
            )
        ]

        # x, y, z: distance, visited
        record = {cube.origin: (math.inf, False) for cube in enclosing_cubes}
        record[origin] = (0, False)

        def unvisited_neighbours(cube):
            x, y, z = cube.origin
            candidates = (
                Cube(x + 1, y, z),
                Cube(x - 1, y, z),
                Cube(x, y + 1, z),
                Cube(x, y - 1, z),
                Cube(x, y, z + 1),
                Cube(x, y, z - 1),
            )
            return (
                c for c in candidates
                if c.origin in record and not record[c.origin][1]  # unvisited
            )

        contour = []
        current = Cube(*origin)
        while current:
            current_distance, _ = record[current.origin]

            for neighbour in unvisited_neighbours(current):

                if neighbour in self:  # We've hit a surface cube

                    # Determine sides overlapping with the current
                    # cube on the exterior, the surface sides of the
                    # collection.
                    for side in neighbour.sides:
                        if side in current and side not in contour:
                            contour.append(side)

                else:
                    record[neighbour.origin] = current_distance + 1, False


            # Mark current node as visisted and determine next one
            record[current.origin] = current_distance, True
            current = min(
                (
                    Cube(*point) for point in record
                    if not record[point][1] and record[point][0] < math.inf  # unvisited and finite distance
                ),
                key=lambda cube: record[cube.origin][0],
                default=None
            )

        return contour


def parse_input(path: str = "input.txt") -> CubeCollection:
    with open(path, "r") as fp:
        lines = [line.strip().split(",") for line in fp.readlines()]

    def origins():
        for x, y, z in lines:
            yield int(x), int(y), int(z)

    return CubeCollection([Cube(*origin) for origin in origins()])


def main(path: str = "input.txt"):
    cc = parse_input(path)
    # Part 1
    print(f"The number of free sides in the cube collection is: {cc.free_surface_area()}")

    # Part 2
    print(f"The number of exterior sides in the cube collection is: {cc.exterior_surface_area()}")

if __name__ == "__main__":
    main()
