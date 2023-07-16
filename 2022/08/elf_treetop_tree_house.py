from functools import reduce
from typing import Callable


class TreeAlreadyExistsError(Exception):
    pass


class Tree:
    """A representation of a tree in the grid."""

    def __init__(self, grid: "TreeGrid", position: tuple[int, int], height: int):
        self.grid = grid
        self.height = height
        self.position = position

    @property
    def visible(self) -> bool:
        return any(
            map(
                lambda height: height < self.height,
                self.get_tallest_neighbour_heights(),
            )
        )

    @property
    def scenic_score(self) -> int:
        return reduce(lambda x, y: x * y, self.get_view_distances())

    def __str__(self):
        return (
            f"Tree at: {self.position}\n"
            f"   Height: {self.height}\n"
            f"   Visible: {self.visible}\n"
            f"   Scenic score: {self.scenic_score}"
        )

    def get_tallest_neighbour_heights(self) -> tuple[int, int, int, int]:
        """Return the maximum height of all neighbours in the grid located
        respectivly to the left, above, right and below the current tree.

        If the tree is at the edge of the grid, the height of its nonexistant
        neighbour will be reported as -1.
        """

        def max_height_in_selected_range(
            pos_func: Callable[[int], tuple[int, int]], tree_range: range
        ) -> int:
            return max(
                map(
                    lambda tree: tree.height,
                    filter(None, [self.grid.get_tree(pos_func(i)) for i in tree_range]),
                ),
                default=-1,
            )

        left = max_height_in_selected_range(
            lambda i: (self.position[0], i), range(0, self.position[1])
        )

        right = max_height_in_selected_range(
            lambda i: (self.position[0], i),
            range(self.position[1] + 1, self.grid.columns),
        )

        up = max_height_in_selected_range(
            lambda i: (i, self.position[1]), range(0, self.position[0])
        )

        down = max_height_in_selected_range(
            lambda i: (i, self.position[1]), range(self.position[0] + 1, self.grid.rows)
        )

        return left, up, right, down

    def get_view_distances(self) -> tuple[int, int, int, int]:
        """Return the view distance along each axis of the grid. Respectivly,
        to the left, above, right and below the current tree.
        """

        def get_view_distance(pos_func, i):
            tree = self.grid.get_tree(pos_func(i))
            if tree is None:
                return 0

            if tree.height >= self.height:
                return 1

            return 1 + get_view_distance(pos_func, i + 1)

        left = get_view_distance(lambda i: (self.position[0], self.position[1] - i), 1)

        right = get_view_distance(lambda i: (self.position[0], self.position[1] + i), 1)

        up = get_view_distance(lambda i: (self.position[0] - i, self.position[1]), 1)

        down = get_view_distance(lambda i: (self.position[0] + i, self.position[1]), 1)

        return left, up, right, down


class TreeGrid:
    """A representation of tree's in a grid. Each tree is uniquely identified
    by a pair of coordinates describing its position in the grid. The grid is
    zero indexed with the tree in the leftmost-topmost corner having position
    (0,0).

    The first coordinate identifies a tree's vertical (up/down) position in the
    grid. While the second identifies its horizontal (left/right) position in
    the gird.
    """

    def __init__(self, rows: int, columns: int):
        self.rows = rows
        self.columns = columns
        self.tree_map = {}

    @property
    def total_trees(self) -> int:
        return len(self.tree_map.values())

    @property
    def visible_trees(self) -> int:
        return sum(
            map(
                lambda tree: 1 if tree.visible else 0,
                [tree for tree in self.tree_map.values()],
            )
        )

    @property
    def invisible_trees(self) -> int:
        return self.total_trees - self.visible_trees

    @property
    def highest_scenic_score(self) -> Tree:
        return max(
            [tree for tree in self.tree_map.values()],
            key=lambda tree: tree.scenic_score,
        )

    def insert_tree(self, position: tuple[int, int], height: int) -> Tree:
        """Insert at tree at position in the grid."""
        if self.get_tree(position) is not None:
            raise TreeAlreadyExistsError

        self.tree_map[position] = Tree(self, position, height)

    def get_tree(self, position: tuple[int, int]) -> Tree | None:
        return self.tree_map.get(position)

    def print_grid(self):
        for tree in self.tree_map.values():
            print(tree)


def get_trees(puzzle_input: str = "input.txt") -> TreeGrid:
    """Parse the input at puzzle_input and return a tree gird."""
    with open(puzzle_input) as f:
        lines = []
        line = f.readline()
        while line != "":
            lines.append(line)
            line = f.readline()

    coulmns = len(lines[0]) - 1  # Get rid of final newline char
    rows = len(lines)
    grid = TreeGrid(rows, coulmns)

    for r in range(rows):
        for c in range(coulmns):
            grid.insert_tree((r, c), int(lines[r][c]))

    return grid


if __name__ == "__main__":
    grid = get_trees()
    print(
        (
            f"The grid contains: {grid.total_trees} trees.\n"
            f"The number of visible trees is: {grid.visible_trees}.\n"
            f"The number of invisible trees is: {grid.invisible_trees}.\n"
            "The highest scenic score is: "
            f"{grid.highest_scenic_score.scenic_score}."
        )
    )

    print(
        "The tree with the highest scenic score is:\n"
        f"{grid.highest_scenic_score}"
    )
