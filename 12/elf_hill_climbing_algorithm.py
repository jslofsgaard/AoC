from typing import Optional
import time

Point = tuple[int, int]
Path = list[Point]


class Colors:
    red = '\033[31m'
    blue = '\033[34m'
    black = '\033[30m'
    default = '\033[39m'


class PathFinder:
    def __init__(self, grid: "Grid", debug: bool = False):
        self.grid = grid
        self.debug = debug

    def find_path(self) -> Path:
        def get_step(current: Point) -> Optional[Point]:
            steps = [
                step for step in self.grid.cardinals(current)
                if step not in walked and
                self.grid.height(step) - self.grid.height(current) <= 1
            ]
            return min(
                steps,
                key=lambda step: (
                    abs(self.grid.end[0] - step[0]) +
                    abs(self.grid.end[1] - step[1])
                ),
                default=None
            )

        walked = [self.grid.start]
        path = [self.grid.start]
        while path and path[-1] != self.grid.end:

            if self.debug:
                self.grid.print_grid(self.get_chart(path))
                time.sleep(0.01)

            # can we advance somewhere?
            step = get_step(path[-1])
            if step is not None:
                path.append(step)
                walked.append(step)
                continue

            # we cannot advance, backtrack
            path.pop()

        return path

    def shorten_path(self, path: Path) -> Path:
        def get_link(walked: Path) -> Optional[Point]:
            links = [
                link for link in self.grid.cardinals(walked[-1])
                if link in walked[:-2] and
                self.grid.height(walked[-1]) - self.grid.height(link) <= 1
            ]
            return min(
                links,
                key=lambda link: len(walked[-1]) - len(link),
                default=None
            )

        def get_shorter(path: Path) -> Path:
            walked = []
            for step in path:
                walked.append(step)
                link = get_link(walked)
                if link is not None:
                    start = path.index(link)
                    stop = path.index(step)
                    return path[:start+1] + path[stop:]

            return path

        shortend = get_shorter(path)
        while shortend != path:

            if self.debug:
                self.grid.print_grid(self.get_chart(shortend))
                time.sleep(0.01)

            path = shortend
            shortend = get_shorter(path)

        if self.debug:
            self.grid.print_grid(self.get_chart(path))
            time.sleep(0.01)

        return path

    def get_chart(self, path: Path) -> dict[Point, str]:
        def get_marking(step: Point, next_step: Point) -> str:
            if next_step[0] - step[0] == -1:  # Is next step above?
                return Colors.red + '↑' + Colors.default

            elif next_step[0] - step[0] == 1:  # Is next step below?
                return Colors.red + '↓' + Colors.default

            elif next_step[1] - step[1] == 1:  # Is next step to the right?
                return Colors.red + '→' + Colors.default

            elif next_step[1] - step[1] == -1:  # Is next step to the left?
                return Colors.red + '←' + Colors.default

            else:
                raise Exception('Next step is not adjacent!')

        chart = {}
        filtered = list(filter(
                lambda step: step not in (self.grid.start, self.grid.end),
                path
        ))
        for step, next_step in zip(filtered[:-1],  filtered[1:]):
            chart[step] = get_marking(step, next_step)

        if path[-1] != self.grid.end:
            chart[path[-1]] = Colors.blue + 'X' + Colors.default
        else:
            chart[path[-2]] = get_marking(path[-2], path[-1])

        return chart


class Grid:
    def __init__(
            self,
            proto_grid: list[list[int]],
            start: Point,
            end: Point,
    ):
        self.grid = tuple(tuple(row) for row in proto_grid)
        self.start = start
        self.end = end

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def columns(self) -> int:
        return len(self.grid[0])

    @property
    def coordinates(self) -> int:
        return len(self.grid) * len(self.grid[0])

    def __str__(self) -> str:
        return (
            f'Grid with {self.rows} rows, {self.columns} columns '
            f'yielding a total of {self.coordinates} possible coordinates.'
        )

    @property
    def grid_str(self) -> list[list[str]]:
        height_to_char = {
            0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h',
            8: 'i', 9: 'j', 10: 'k', 11: 'l', 12: 'm', 13: 'n', 14: 'o',
            15: 'p', 16: 'q', 17: 'r', 18: 's', 19: 't', 20: 'u', 21: 'v',
            22: 'w', 23: 'x', 24: 'y', 25: 'z'
        }
        string_grid = [
            [
                Colors.default + height_to_char[height] + Colors.default
                for height in row
            ]
            for row in self.grid
        ]
        string_grid[self.start[0]][self.start[1]] = \
            Colors.blue + 'S' + Colors.default

        string_grid[self.end[0]][self.end[1]] = \
            Colors.blue + 'E' + Colors.default

        return string_grid

    def height(self, point: Point) -> int:
        """Return the height in the grid at point. Points outside the grid are
        assigned a height of 100.
        """
        if (
                point[0] in range(0, self.rows) and
                point[1] in range(0, self.columns)
        ):
            return self.grid[point[0]][point[1]]

        return 100

    def cardinals(self, point: Point) -> list[Point]:
        """Return the points to the left, right, above and below point."""
        return [
            (point[0], point[1] + 1),
            (point[0] - 1, point[1]),
            (point[0] + 1, point[1]),
            (point[0], point[1] - 1)
        ]

    def print_grid(self, *charts: dict[Point, str]) -> None:
        grid = self.grid_str

        for chart in charts:
            for coord, val in chart.items():
                grid[coord[0]][coord[1]] = val

        print('+' + ''.join(['-' for _ in range(self.columns)]) + '+')

        for string_row in grid:
            print('|' + ''.join(string_row) + '|')

        print('+' + ''.join(['-' for _ in range(self.columns)]) + '+')


def parse_line(line: str) -> list[int]:
    char_height = {
        'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8,
        'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16,
        'r': 17, 's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23, 'y': 24,
        'z': 25,

        # Start at lowest height, End at highest.
        'S': 0, 'E': 25
    }
    heights = []
    for char in line.strip():
        heights.append(char_height[char])

    return heights


def get_grid(puzzle_input: str = 'input.txt', debug: bool = False) -> Grid:
    grid = []
    with open(puzzle_input) as f:
        line = f.readline()
        while line:
            grid.append(parse_line(line))

            if line.find('S') != -1:
                start = (len(grid) - 1, line.find('S'))

            if line.find('E') != -1:
                end = (len(grid) - 1, line.find('E'))

            line = f.readline()

    return Grid(grid, start, end)


if __name__ == '__main__':
    grid = get_grid()
    grid.print_grid()

    response = input('Find path to summit? [Y/n]: ')
    while response not in ('Y', 'y', 'N', 'n'):
        response = input('Please answer Y[es] or [n]o: ')

    if response in ('Y', 'y'):
        finder = PathFinder(grid, True)
        path = finder.shorten_path(finder.find_path())
        print(f'Length of found path: {len(path)}')
