from io import TextIOWrapper
from copy import deepcopy


Instruction = tuple[int, int, int]


class SupplyStack:
    def __init__(self, stacks: list[list[str]]) -> None:
        self.stacks = stacks

    def do_instruction_9000(
            self,
            repeat: int,
            from_index: int,
            to_index: int
    ) -> None:
        """Perform the provided instruction on the stacks in accordance with
        how the CrateMover 9000 operates."""
        for _ in range(repeat):
            self.stacks[to_index].append(self.stacks[from_index].pop())

    def do_instruction_9001(
            self,
            count: int,
            from_index: int,
            to_index: int
    ) -> None:
        """Perform the provided instruction on the stacks in accordance with
        how the CrateMover 9001 operates."""
        self.stacks[to_index].extend(self.stacks[from_index][-count:])
        del self.stacks[from_index][-count:]

    def get_top_crates(self) -> str:
        """Return a string containing the ids of all the crates on the top of
        each stack.

        If a stack has no crates in it, its posititon in the returned string is
        replaced with a string,
        """
        top = ''
        for stack in self.stacks:
            try:
                top += stack[-1]
            except IndexError:
                top += ' '

        return top

    def draw(self) -> None:
        """Print a drawing of the supply stacks."""
        lines = []

        num_row = ''
        num_rows = len(self.stacks)
        for i in range(num_rows):
            num_row += ' ' + str(i + 1) + ' '

            if i != num_rows:
                num_row += ' '

        lines.append(num_row)

        tallest = max(map(lambda stack: len(stack), self.stacks))
        for i in range(tallest):
            line = ''
            for stack in self.stacks:
                try:
                    line += '[' + stack[i] + ']'
                except IndexError:
                    line += '   '

                if i != tallest:
                    line += ' '

            lines.append(line)

        lines.reverse()
        for line in lines:
            print(line)


def parse_drawing(fd: TextIOWrapper) -> SupplyStack:
    """Parse the drawing at the beginnig of the input and return the
    corresponding SupplyStack.
    """
    def get_lines() -> list[str]:
        lines = []
        line = fd.readline()
        while line != '\n':
            lines.append(line)
            line = fd.readline()

        return lines

    def get_positions(line: str) -> list[int]:
        """Applied to the lowest row on the drawing, return the positions in
        each string for each number.
        """
        return [line.find(num) for num in line.split()]

    def get_contents(position: int, lines: list[str]) -> list[str]:
        """Provided a postiton in each line, return a list of crates found at
        postiton in each line.
        """
        return [
            line[position] for line in lines
            if line[position].isalpha()
        ]

    lines = get_lines()
    positions = get_positions(lines.pop())
    lines.reverse()
    stacks = [get_contents(position, lines) for position in positions]

    return SupplyStack(stacks)


def parse_instruction(line: str) -> Instruction:
    if line:
        contents = line.split()
        return int(contents[1]), int(contents[3]) - 1, int(contents[5]) - 1

    return None


def get_stack_and_instructions(
        puzzle_input: str = 'input.txt'
) -> tuple[SupplyStack, list[Instruction]]:
    """Construct a supply stack and list of instructions from the input located
    at puzzle_input.
    """
    with open(puzzle_input) as f:
        stack = parse_drawing(f)
        instructions = []
        instruction = parse_instruction(f.readline())
        while instruction:
            instructions.append(instruction)
            instruction = parse_instruction(f.readline())

        return stack, instructions


if __name__ == '__main__':
    supplystack1, instructions = get_stack_and_instructions()
    supplystack2 = deepcopy(supplystack1)
    for instruction in instructions:
        supplystack1.do_instruction_9000(*instruction)

    print("The result of appling the CrateMover 9000 is:")
    supplystack1.draw()
    print(f"The top row is: {supplystack1.get_top_crates()}")

    for instruction in instructions:
        supplystack2.do_instruction_9001(*instruction)

    print("The result of appling the CrateMover 9001 is:")
    supplystack2.draw()
    print(f"The top row is: {supplystack2.get_top_crates()}")
