import multiprocessing
from typing import Iterable

Coordinate = tuple[int, int]
HORIZ = 2_000_000
BOUND = 4_000_000


def parse_input(path="input.txt") -> list["Sensor"]:
    sensors = []
    with open(path, "r") as fp:
        line = fp.readline()
        while line:
            contents = line.split()
            sx, sy = int(contents[2][2:-1]), int(contents[3][2:-1])
            bx, by = int(contents[-2][2:-1]), int(contents[-1][2:])
            sensors.append(Sensor(location=(sx, sy), beacon=(bx, by)))
            line = fp.readline()

    return sensors


def distance(p1, p2):
    x_1, y_1 = p1
    x_2, y_2 = p2
    return abs(x_1 - x_2) + abs(y_1 - y_2)


class Sensor:
    def __init__(self, location: Coordinate, beacon: Coordinate):
        self.location = location
        self.beacon = beacon

    def __repr__(self):
        return f"Sensor(location={self.location}, closest_beacon={self.beacon})"

    def distance(self, x: int, y: int) -> int:
        return distance(self.location, (x, y))

    @property
    def beacon_distance(self):
        return self.distance(*self.beacon)

    def is_covered(self, x: int, y: int) -> bool:
        return self.distance(x, y) <= self.beacon_distance

    def cross_horizontal(self, x: int, y: int) -> Coordinate:
        res = (
            self.location[0] + (self.beacon_distance - abs(y - self.location[1])) + 1,
            y,
        )
        assert self.distance(*res) == self.beacon_distance + 1
        return res


class GridError(Exception):
    pass


class Grid:
    def __init__(self, sensors: Iterable[Sensor]):
        self.sensors = tuple(sensors)

    def __repr__(self):
        return f"Grid({self.sensors})"

    @property
    def x_range(self) -> Coordinate:
        return (
            min(sensor.location[0] - sensor.beacon_distance for sensor in self.sensors),
            max(sensor.location[0] + sensor.beacon_distance for sensor in self.sensors),
        )

    @property
    def y_range(self) -> Coordinate:
        return (
            min(sensor.location[1] - sensor.beacon_distance for sensor in self.sensors),
            max(sensor.location[1] + sensor.beacon_distance for sensor in self.sensors),
        )

    def is_covered(self, x: int, y: int) -> bool:
        return any(sensor.is_covered(x, y) for sensor in self.sensors)

    def is_beacon(self, x: int, y: int) -> bool:
        return any(sensor.beacon == (x, y) for sensor in self.sensors)

    # Must be at the top level for multiprocessing
    def _line_search(self, args: tuple[int, int, int]) -> Coordinate | None:
        x_min, x_max, y = args
        assert x_min < x_max

        point = (x_min, y)
        while self.is_covered(*point):
            point = max(
                (
                    sensor.cross_horizontal(*point)
                    for sensor in self.sensors
                    if sensor.is_covered(*point)
                ),
                key=lambda candidate: candidate[0] - point[0],
            )
            if x_max < point[0]:
                return None

        return point

    def distress_beacon_search(
        self, x_range: Coordinate, y_range: Coordinate
    ) -> Coordinate:
        x_min, x_max = x_range[0], x_range[1]
        y_min, y_max = y_range[0], y_range[1]
        assert x_min < x_max
        assert y_min < y_max

        with multiprocessing.Pool(max(multiprocessing.cpu_count() - 2, 1)) as pool:
            for solution in pool.imap_unordered(
                self._line_search,
                ((x_min, x_max, y) for y in range(y_min, y_max + 1)),
                chunksize=BOUND // 40,
            ):
                if solution is not None:
                    return solution
            else:
                raise GridError("No distress beacon found")


def tuning_frequency(x: int, y: int) -> int:
    return x * BOUND + y


if __name__ == "__main__":
    # Part 1
    grid = Grid(parse_input())
    min_x, max_x = grid.x_range
    covered_positions = sum(
        1 if not grid.is_beacon(x, HORIZ) and grid.is_covered(x, HORIZ) else 0
        for x in range(min_x, max_x + 1)
    )
    print(
        f"In the row y={HORIZ} the total number of positions which cannot contain a beacon is: {covered_positions}"
    )

    # Part 2
    distress_beacon = grid.distress_beacon_search((0, BOUND), (0, BOUND))
    print(
        f"The distress beacon is at {distress_beacon}, its tuning frequency is: {tuning_frequency(*distress_beacon)}"
    )
