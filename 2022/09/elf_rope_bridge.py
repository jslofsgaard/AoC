Instruction = tuple[str, int]
Position = tuple[int, int]


class Rope:
    def __init__(self, knots: int = 2, pos: Position = (0, 0)):
        if knots < 1:
            raise ValueError("A rope must at minimum have 2 knots!")

        self.knot = [pos for _ in range(knots)]
        self.knot_history = [[pos] for _ in range(knots)]

    @property
    def head(self) -> Position:
        return self.knot[0]

    @property
    def tail(self) -> Position:
        return self.knot[-1]

    @property
    def unique_positions(self) -> list[set[Position]]:
        return [set(history) for history in self.knot_history]

    @property
    def unique_head_positions(self) -> set[Position]:
        return self.unique_positions[0]

    @property
    def unique_tail_positions(self) -> set[Position]:
        return self.unique_positions[-1]

    def adjacent(self, knot1: Position, knot2: Position) -> bool:
        if abs(knot1[0] - knot2[0]) > 1 or abs(knot1[1] - knot2[1]) > 1:
            return False

        return True

    def move(self, ins: Instruction) -> None:
        """Move the head of the rope according to the instruction. The remaning
        knots down to the tail may or may not be moved as a consequence.

        If the position of a knot changes, it is recorded in the knots position
        history.
        """

        def move_head(direction: str):
            movement_map = {
                "R": lambda h: (h[0], h[1] + 1),
                "L": lambda h: (h[0], h[1] - 1),
                "U": lambda h: (h[0] + 1, h[1]),
                "D": lambda h: (h[0] - 1, h[1]),
            }

            self.knot[0] = movement_map[direction](self.knot[0])
            self.knot_history[0].append(self.knot[0])

        def ripple_movment():
            for i in range(1, len(self.knot)):
                if not self.adjacent(self.knot[i - 1], self.knot[i]):
                    delta = (
                        self.knot[i - 1][0] - self.knot[i][0],
                        self.knot[i - 1][1] - self.knot[i][1],
                    )
                    self.knot[i] = (
                        self.knot[i][0] + sgn(delta[0]),
                        self.knot[i][1] + sgn(delta[1]),
                    )
                    self.knot_history[i].append(self.knot[i])

        for _ in range(ins[1]):
            move_head(ins[0])
            ripple_movment()


def sgn(x: int) -> int:
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0


def parse_line(line: str) -> Instruction:
    """Parse an input line and return a tuple where the first coordinate is the
    direction to move, while the second coordinate is the amount of steps to
    move.
    """
    return (line.split()[0], int(line.split()[1]))


def get_instructions(puzzle_input: str = "input.txt") -> list[Instruction]:
    """Parse the input at puzzle_input and return a list of rope movment
    instructions.
    """
    with open(puzzle_input) as f:
        instructions = []
        line = f.readline()
        while line != "":
            instructions.append(parse_line(line))
            line = f.readline()

    return instructions


if __name__ == "__main__":
    rope = Rope()
    instructions = get_instructions()
    for instruction in instructions:
        rope.move(instruction)

    print(
        (
            "For a 2 knot rope we have that:\n"
            f"   The final position of the head is: {rope.head}\n"
            f"   The final position of the tail is: {rope.tail}\n"
            f"   Number of unique head positions reached: "
            f"{len(rope.unique_head_positions)}\n"
            f"   Number of unique tail positions reached: "
            f"{len(rope.unique_tail_positions)}\n"
        )
    )

    rope = Rope(10)
    instructions = get_instructions()
    for instruction in instructions:
        rope.move(instruction)

    print(
        (
            "For a 10 knot rope we have that:\n"
            f"   The final position of the head is: {rope.head}\n"
            f"   The final position of the tail is: {rope.tail}\n"
            f"   Number of unique head positions reached: "
            f"{len(rope.unique_head_positions)}\n"
            f"   Number of unique tail positions reached: "
            f"{len(rope.unique_tail_positions)}\n"
        )
    )

    rope = Rope(100)
    instructions = get_instructions()
    for instruction in instructions:
        rope.move(instruction)

    print(
        (
            "For a 100 knot rope we have that:\n"
            f"   The final position of the head is: {rope.head}\n"
            f"   The final position of the tail is: {rope.tail}\n"
            f"   Number of unique head positions reached: "
            f"{len(rope.unique_head_positions)}\n"
            f"   Number of unique tail positions reached: "
            f"{len(rope.unique_tail_positions)}\n"
        )
    )
