from typing import Callable


Instruction = tuple[str, int]
ExecutingInstruction = dict[str, int | Callable[[int], None]]


class Device:
    def __init__(
        self,
        instruction_queue: list,
        record_at: list[int],
        X: int = 1,
    ):
        self.X = X
        self.signal_strengths = []
        self.record_at = record_at
        self.instruction_queue = instruction_queue
        self.executing_instruction = None
        self.cycle = 0
        self.pixels = [["." for _ in range(40)] for _ in range(6)]

    @property
    def instructions_remaning(self) -> bool:
        if self.instruction_queue:
            return True
        return False

    @property
    def sprite(self) -> tuple[int, int, int]:
        return (self.X - 1, self.X, self.X + 1)

    def addx(self, arg: int) -> None:
        self.X += arg

    def noop(self, arg: int) -> None:
        pass

    def start_instruction(self, ins: Instruction) -> ExecutingInstruction:
        if ins[0] == "noop":
            return {"remaning_cycles": 1, "instruction": self.noop, "arg": ins[1]}

        return {"remaning_cycles": 2, "instruction": self.addx, "arg": ins[1]}

    @property
    def crt_position(self) -> tuple[int, int]:
        return (((self.cycle - 1) % 240) // 40, ((self.cycle - 1) % 240) % 40)

    def draw_pixel(self) -> None:
        if self.crt_position[1] in self.sprite:
            self.pixels[self.crt_position[0]][self.crt_position[1]] = "#"
        else:
            self.pixels[self.crt_position[0]][self.crt_position[1]] = "."

    def render(self) -> str:
        for row in self.pixels:
            print("".join(row))

    def run_cycle(self) -> None:
        self.cycle += 1

        # Start next instruction if none
        if self.executing_instruction is None:
            self.executing_instruction = self.start_instruction(
                self.instruction_queue.pop()
            )

        # Record signal strength during cycle?
        if self.cycle in self.record_at:
            self.signal_strengths.append((self.cycle, self.X * self.cycle))

        # Draw pixel
        self.draw_pixel()

        # One cycle done, finish instruction?
        self.executing_instruction["remaning_cycles"] -= 1
        if self.executing_instruction["remaning_cycles"] == 0:
            self.executing_instruction["instruction"](self.executing_instruction["arg"])
            self.executing_instruction = None


def parse_line(line: str) -> Instruction:
    x = line.split()
    if x[0] == "noop":
        return ("noop", 0)

    return ("addx", int(x[1]))


def get_instructions(puzzle_input: str = "input.txt") -> list[Instruction]:
    with open(puzzle_input) as f:
        instructions = []
        line = f.readline()
        while line:
            instructions.append(parse_line(line))
            line = f.readline()

    return list(reversed(instructions))


if __name__ == "__main__":
    device = Device(get_instructions(), [20, 60, 100, 140, 180, 220])

    while device.instructions_remaning:
        device.run_cycle()

    print(f"Number of cycles ran until instructions exhausted: {device.cycle}")
    print("Recorded signal strenghts:")
    for record in device.signal_strengths:
        print(f"   cycle: {record[0]}, signal strenght: {record[1]}")

    print(
        (
            "Sum recorded signal strenghts: "
            f"{sum([record[1] for record in device.signal_strengths])}"
        )
    )
    print()
    device.render()
