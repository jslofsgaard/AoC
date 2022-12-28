import time
import itertools
from typing import Optional

Point = tuple[int, int]


CLIMB = 1


class Colors:
    red = '\033[31m'
    green = '\033[32m'
    blue = '\033[34m'
    magenta = '\033[35m'
    cyan = '\033[36m'
    black = '\033[30m'
    default = '\033[39m'


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
    def nrow(self) -> int:
        return len(self.grid)

    @property
    def ncol(self) -> int:
        return len(self.grid[0])

    @property
    def points(self) -> int:
        return tuple(itertools.product(range(self.nrow), range(self.ncol)))

    @property
    def npoints(self) -> int:
        return len(self.points)

    def __str__(self) -> str:
        return (
            f'Grid with {self.nrow} rows, {self.ncol} columns '
            f'yielding a total of {self.npoints} points.'
        )

    def stringify(self) -> list[list[str]]:
        """Return a string representation of the grid where each height is
        translated back into a char.
        """
        height_to_char = {
            0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h',
            8: 'i', 9: 'j', 10: 'k', 11: 'l', 12: 'm', 13: 'n', 14: 'o',
            15: 'p', 16: 'q', 17: 'r', 18: 's', 19: 't', 20: 'u', 21: 'v',
            22: 'w', 23: 'x', 24: 'y', 25: 'z'
        }
        out = [
            [height_to_char[height] for height in row]
            for row in self.grid
        ]
        out[self.start[0]][self.start[1]] = \
            Colors.cyan + 'S' + Colors.default

        out[self.end[0]][self.end[1]] = \
            Colors.cyan + 'E' + Colors.default

        return out

    def height(self, point: Point) -> int:
        """Return the height in the grid at point."""
        if point not in self.points:
            raise ValueError('Point not in grid!')

        return self.grid[point[0]][point[1]]

    def elevation(self, from_point: Point, to_point: Point) -> int:
        """Return the height difference in *moving* from from_point to
        to_point.
        """
        if from_point not in self.points or to_point not in self.points:
            raise ValueError('Point not in grid!')

        return self.height(to_point) - self.height(from_point)

    def cardinals(self, point: Point) -> list[Point]:
        """Return points in grid adjacent (left, right, above, below) to point.
        """
        return [
            point for point in [
                (point[0], point[1] + 1),
                (point[0] - 1, point[1]),
                (point[0] + 1, point[1]),
                (point[0], point[1] - 1)
            ]
            if point in self.points
        ]

    def print(self, *paths: 'Path') -> None:
        """Print the string representation of gird with each path layerd on top
        successively.
        """
        grid = self.stringify()

        for path in paths:
            for point, sym in path.chart().items():
                grid[point[0]][point[1]] = sym

        print('+' + ''.join(['-' for _ in range(self.ncol)]) + '+')

        for row in grid:
            print('|' + ''.join(row) + '|')

        print('+' + ''.join(['-' for _ in range(self.ncol)]) + '+')


class Path:
    def __init__(self, grid: Grid, proto_path: list[Point]):
        self.grid = grid
        self.path = tuple(proto_path)

    @property
    def length(self) -> int:
        return len(self.path)

    @property
    def valid(self) -> bool:
        for point, next_point in zip(self.path[:-1], self.path[1:]):
            if not (
                    next_point in self.grid.cardinals(point) and
                    self.grid.elevation(point, next_point) <= CLIMB
            ):
                return False

        return True

    @property
    def complete(self) -> bool:
        if not self.path:
            return False

        return all((
            self.valid,
            self.path[0] == self.grid.start,
            self.path[-1] == self.grid.end
        ))

    def chart(self) -> dict[Point, str]:
        chart = {}

        if not self.path:
            return chart

        def arrow(point: Point, next_point: Point) -> str:
            if self.grid.height(point) < 2:
                color = Colors.red
            elif self.grid.height(point) == 2:
                color = Colors.green
            elif 2 < self.grid.height(point) < 10:
                color = Colors.blue
            else:
                color = Colors.magenta

            out = {
                (-1, 0): color + '↑' + Colors.default,
                (1, 0): color + '↓' + Colors.default,
                (0, 1): color + '→' + Colors.default,
                (0, -1): color + '←' + Colors.default
            }
            return out[(next_point[0] - point[0], next_point[1] - point[1])]

        filtered = [
            point for point in self.path
            if point not in (self.grid.start, self.grid.end)
        ]
        for point, next_point in zip(filtered[:-1],  filtered[1:]):
            chart[point] = arrow(point, next_point)

        if self.path[-1] != self.grid.end:
            chart[self.path[-1]] = Colors.cyan + 'X' + Colors.default
        else:
            chart[self.path[-2]] = arrow(self.path[-2], self.path[-1])

        return chart


class Seeker:
    def __init__(self, grid: Grid, visual: bool = False):
        self.grid = grid
        self.path = []
        self.walked = []
        self.visual = visual

    def print(self) -> None:
        print('\033[2J\033[H', end='')  # Clear screen on terminal
        self.grid.print(Path(self.grid, self.path))

    def search(self) -> Path:
        self.walked.append(self.grid.start)
        self.path.append(self.grid.start)

        while self.path and self.path[-1] != self.grid.end:
            step = self.get_step(self.path[-1])  # can we advance somewhere?
            if step is not None:
                self.path.append(step)
                self.walked.append(step)

            else:  # we cannot advance, backtrack
                self.path.pop()

        return self.refine()

    def get_step(self, point: Point) -> Optional[Point]:
        steps = [
            step for step in self.grid.cardinals(point)
            if step not in self.walked and
            self.grid.elevation(point, step) <= CLIMB
        ]
        return min(steps, key=self.metric, default=None)

    def metric(self, point: Point) -> int:
        """Returns the distance of step from the end point in the grid. The
        horisontal and vertical distances are weighted according to the the
        number of rows and columns in the grid.
        """
        nrow = self.grid.nrow
        ncol = self.grid.ncol
        tot = nrow + ncol
        return (
            (nrow/tot) * abs(point[0] - self.grid.end[0]) +
            (ncol/tot) * abs(point[1] - self.grid.end[1])
        )

    def refine(self) -> Path:
        if self.path:
            i = 0
            while self.path[i] != self.grid.end:
                i += 1

                loopback = self.get_loopback(i)
                if loopback is not None:
                    j = self.path.index(loopback)
                    self.path = self.path[:j+1] + self.path[i:]
                    i = j

                if self.visual:
                    self.print()

        return Path(self.grid, self.path)

    def get_loopback(self, index: int) -> Optional[Point]:
        loopbacks = [
            point for point in self.grid.cardinals(self.path[index])
            if point in self.path[:index-1] and
            self.grid.elevation(point, self.path[index]) <= CLIMB
        ]

        return min(loopbacks, key=self.step_count, default=None)

    def step_count(self, point: Point) -> int:
        return self.path.index(point)


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
    grid.print()

    response = input('Find path to summit with Seeker algorithm? [Y/n]: ')
    while response not in ('Y', 'y', 'N', 'n'):
        response = input('Please answer Y[es] or [n]o: ')

    if response in ('Y', 'y'):
        visual = input('Show the algorithm visually? [Y/n]: ')
        while response not in ('Y', 'y', 'N', 'n'):
            visual = input('Please answer Y[es] or [n]o: ')

        if visual in ('Y', 'y'):
            finder = Seeker(grid, True)
        else:
            finder = Seeker(grid)
        start = time.time()
        path = finder.search()
        stop = time.time()
        print(f'Path length : {path.length}')
        print(f'Path is valid: {path.valid}')
        print(f'Path is complete: {path.complete}')
        print(f'Time to find path: {stop - start}')
        grid.print(path)
