from typing import Iterable


Coordinate = tuple[int, int]
HORIZ = 2000000


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
