import itertools
import math
import time
from dataclasses import dataclass
from typing import Iterator, Optional, Self

Point = tuple[int, int]

CLIMB_HEIGHT = 1

CHAR_HEIGHT = {
    'a': 0,
    'b': 1,
    'c': 2,
    'd': 3,
    'e': 4,
    'f': 5,
    'g': 6,
    'h': 7,
    'i': 8,
    'j': 9,
    'k': 10,
    'l': 11,
    'm': 12,
    'n': 13,
    'o': 14,
    'p': 15,
    'q': 16,
    'r': 17,
    's': 18,
    't': 19,
    'u': 20,
    'v': 21,
    'w': 22,
    'x': 23,
    'y': 24,
    'z': 25,
    'S': 0,  # Start at lowest height
    'E': 25  # End at highest
}


class Colors:
    red = '\033[31m'
    green = '\033[32m'
    blue = '\033[34m'
    magenta = '\033[35m'
    cyan = '\033[36m'
    black = '\033[30m'
    default = '\033[39m'


class Grid:
    """Handles the boring aspects of the grid data, providing some methods to query
    properties of the grid and printing it.

    """
    def __init__(
            self,
            grid: Iterator[Iterator[int]],
            start: Point,
            end: Point,
    ):
        self.grid = tuple(tuple(row) for row in grid)
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return (
            f'Grid with {self.nrow} rows, {self.ncol} columns '
            f'yielding a total of {self.npoints} points.'
        )

    def _char_grid(self) -> list[list[str]]:
        """A string representation of the grid where each height is represented by a
        character.

        """
        height_to_char = {v: k for k,v in CHAR_HEIGHT.items() if k not in ('S', 'E')}
        out = [
            [height_to_char[height] for height in row]
            for row in self.grid
        ]

        # Special chars and colors for start and end
        out[self.start[0]][self.start[1]] = Colors.cyan + 'S' + Colors.default
        out[self.end[0]][self.end[1]] = Colors.cyan + 'E' + Colors.default

        return out

    @classmethod
    def from_puzzle(cls, puzzle_input: str = 'input.txt') -> Self:

        def parse_line(line: str) -> list[int]:
            return [CHAR_HEIGHT[char] for char in line.strip()]

        with open(puzzle_input) as f:
            grid = []
            line = f.readline()
            while line:
                grid.append(parse_line(line))

                if line.find('S') != -1:
                    start = (len(grid) - 1, line.find('S'))

                if line.find('E') != -1:
                    end = (len(grid) - 1, line.find('E'))

                line = f.readline()

        return Grid(grid, start, end)

    @property
    def nrow(self) -> int:
        return len(self.grid)

    @property
    def ncol(self) -> int:
        return len(self.grid[0])

    @property
    def npoints(self) -> int:
        return self.nrow * self.ncol

    @property
    def points(self) -> int:
        return tuple(itertools.product(range(self.nrow), range(self.ncol)))

    def height(self, point: Point) -> int:
        """The height in the grid at point."""
        if point not in self.points:
            raise ValueError('Point not in grid!')

        return self.grid[point[0]][point[1]]

    def elevation(self, from_point: Point, to_point: Point) -> int:
        """The height difference in *moving* from from_point to to_point."""
        if from_point not in self.points or to_point not in self.points:
            raise ValueError('Point not in grid!')

        return self.height(to_point) - self.height(from_point)

    def cardinals(self, point: Point) -> list[Point]:
        """Points in grid adjacent (left, right, above, below) to point."""
        return [
            point for point in [
                (point[0], point[1] + 1),
                (point[0] - 1, point[1]),
                (point[0] + 1, point[1]),
                (point[0], point[1] - 1)
            ]
            if point in self.points
        ]

    def print(self, *points: Point) -> None:
        """Print the string representation of the grid with each point
        marked explicitly with an 'X'.

        """
        grid = self._char_grid()

        for point in points:
            grid[point[0]][point[1]] = (
                Colors.cyan
                + grid[point[0]][point[1]]
                + Colors.default
            )

        print('+' + ''.join(['-' for _ in range(self.ncol)]) + '+')

        for row in grid:
            print('|' + ''.join(row) + '|')

        print('+' + ''.join(['-' for _ in range(self.ncol)]) + '+')


class Path:
    """Handles the boring aspects of path data. Supplies methods that check if a path is
    valid, if it is compelete and computes its lenght. Most importantly, provides a
    method for 'charting' a path.

    """
    def __init__(self, grid: Grid, path: Iterator[Point]):
        self.grid = grid
        self.path = tuple(path)

    @property
    def length(self) -> int:
        return len(self.path) - 1  # Start is not considered a part of the path length!

    @property
    def valid(self) -> bool:
        if not self.path: # Is the path empty?
            return False

        for point, next_point in zip(self.path[:-1], self.path[1:]):
            if not (
                    next_point in self.grid.cardinals(point)
                    and self.grid.elevation(point, next_point) <= CLIMB_HEIGHT
            ):
                return False

        return True

    @property
    def complete(self) -> bool:
        return all((
            self.valid,
            self.path[0] == self.grid.start,
            self.path[-1] == self.grid.end
        ))

    def chart(self) -> dict[Point, str]:
        """The chart of the path. Points associated with arrows pointing to the next
        point in the path.

        """
        if not self.path:  # Empty path yields empty chart
            return {}

        def arrow(point: Point, next_point: Point) -> str:
            if self.grid.height(point) < 2:
                color = Colors.red
            elif self.grid.height(point) == 2:
                color = Colors.green
            elif 2 < self.grid.height(point) < 10:
                color = Colors.blue
            else:
                color = Colors.magenta

            direction = {
                (-1, 0): color + '↑' + Colors.default,
                (1, 0): color + '↓' + Colors.default,
                (0, 1): color + '→' + Colors.default,
                (0, -1): color + '←' + Colors.default
            }
            return direction[(next_point[0] - point[0], next_point[1] - point[1])]

        # path without the beginning and end
        inner_path = [
            point for point in self.path
            if point not in (self.grid.start, self.grid.end)
        ]

        if not inner_path:  # Empty inner path, in case path contains only start and/or end
            return {}

        # chart of inner path
        chart = {
            point: arrow(point, next_point)
            for point, next_point in zip(inner_path[:-1], inner_path[1:])
        }

        # if path is not complete, end it with an 'X'
        if self.path[-1] != self.grid.end:
            chart[self.path[-1]] = Colors.cyan + 'X' + Colors.default
        else:
            chart[self.path[-2]] = arrow(self.path[-2], self.path[-1])

        return chart

    def print(self) -> None:
        """Print the string representation of the path layered ontop
        of its grid.

        """
        grid = self.grid._char_grid()

        for point, sym in self.chart().items():
            grid[point[0]][point[1]] = sym

        print('+' + ''.join(['-' for _ in range(self.grid.ncol)]) + '+')

        for row in grid:
            print('|' + ''.join(row) + '|')

        print('+' + ''.join(['-' for _ in range(self.grid.ncol)]) + '+')


class Seeker:
    """A class implementing my own bespoke path finding algorithm. It
    is not optimal, nor does it produce the shortest path. It does,
    however, produce a valid and complete path.

    TODO: cleanup all the code

    """
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
            self.grid.elevation(point, step) <= CLIMB_HEIGHT
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
            self.grid.elevation(point, self.path[index]) <= CLIMB_HEIGHT
        ]

        return min(loopbacks, key=self.step_count, default=None)

    def step_count(self, point: Point) -> int:
        return self.path.index(point)


class DijkstraEmptyPointsError(Exception):
    pass

@dataclass
class DijkstraNode:
    distance: float  = math.inf
    visited: bool = False
    previous: Point | None = None

class Dijkstra:

    def __init__(self, grid: Grid):
        self.grid = grid

    def _unvisited_points(self) -> Iterator[Point]:
        return (
            point for point in self.grid.points
            if self.nodes[point].visited == False
        )

    def _visited_points(self) -> Iterator[Point]:
        return (
            point for point in self.grid.points
            if self.nodes[point].visited == True
        )

    def _closest_point(self, points: Iterator[Point]) -> int:
        try:
            return min(
                points,
                key=lambda point: self.nodes[point].distance
            )
        except ValueError:
            raise DijkstraEmptyPointsError()

    def _unvisited_neighbours(self, point: Point) -> Iterator[Point]:
        return (
            neighbour for neighbour in self.grid.cardinals(point)
            if self.nodes[neighbour].visited == False
        )

    def _backtrack_path(self, point: Point, reverse=False) -> list[Point]:
        path = []
        while point is not None:
            path.append(point)
            point = self.nodes[point].previous

        if reverse:
            return reversed(path)
        else:
            return path

    def search(self) -> Path:
        self.nodes = {
            point: DijkstraNode() for point in self.grid.points
        }
        self.nodes[self.grid.start].distance = 0.0

        def update_distance(neighbour: Point) -> None:
            if (
                    # you can drop down as far as you want!
                    self.grid.elevation(current, neighbour) <= CLIMB_HEIGHT
                    and self.nodes[neighbour].distance > self.nodes[current].distance + 1
            ):
                self.nodes[neighbour].distance = self.nodes[current].distance + 1
                self.nodes[neighbour].previous = current

        while (
                self.nodes[self.grid.end].visited == False
                and self.nodes[self._closest_point(self._unvisited_points())].distance != math.inf
        ):
            current = self._closest_point(self._unvisited_points())
            for neighbour in self._unvisited_neighbours(current):
                update_distance(neighbour)

            self.nodes[current].visited = True

        return Path(self.grid, self._backtrack_path(current, reverse=True))

    def reverse_search(self) -> Path:
        self.nodes = {
            point: DijkstraNode() for point in self.grid.points
        }
        self.nodes[self.grid.end].distance = 0.0

        def update_distance(neighbour: Point) -> None:
            if (
                    self.grid.elevation(neighbour, current) <= CLIMB_HEIGHT
                    and self.nodes[neighbour].distance > self.nodes[current].distance + 1
            ):
                self.nodes[neighbour].distance = self.nodes[current].distance + 1
                self.nodes[neighbour].previous = current

        while self.nodes[self._closest_point(self._unvisited_points())].distance != math.inf:
            current = self._closest_point(self._unvisited_points())
            for neighbour in self._unvisited_neighbours(current):
                update_distance(neighbour)

            self.nodes[current].visited = True

        start = self._closest_point(
            (point for point in self.grid.points if self.grid.height(point) == 0)
        )
        return Path(
            Grid(self.grid.grid, start, self.grid.end),
            self._backtrack_path(start)
        )


def ask(prompt) -> bool:
    ret = input(prompt + ' [Y/n]: ')
    while ret not in ('Y', 'y', 'N', 'n'):
        ret = input('Please answer Y[es] or [n]o: ')

    return True if ret.lower() == 'y' else False

if __name__ == '__main__':

    grid = Grid.from_puzzle()

    def run(finder):
        start = time.time()
        path = finder()
        stop = time.time()
        print(f'Path length : {path.length}')
        print(f'Path is valid: {path.valid}')
        print(f'Path is complete: {path.complete}')
        print(f'Time to find path: {stop - start}')
        path.print()

    use_seeker = ask('Find path to summit with Seeker algorithm?')
    use_dijkstra = ask('Find path to summit with Dijkstra algorithm?')
    use_dijkstra_all = ask('Find best starting position with Dijkstra algorithm?')

    if use_seeker:
        run(Seeker(grid).search)

    if use_dijkstra:
        run(Dijkstra(grid).search)

    if use_dijkstra_all:
        run(Dijkstra(grid).reverse_search)
