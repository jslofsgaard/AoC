"""
Part 2:

Notice that all the tests determining which monkey we throw to next, checks
wether or not our worry level is divisible by some number. Yet, all the
inspection operations increase said worry number. One of them (old * old) quite
rapidly. Meaning that as the number of rounds increases the worry level numbers
will tend towards infinity. Making it effectivly impossible to run 10000 rounds
without somehow decreasing the worry numbers.

The solution is to use modular arithemtic! You can think of the worry numbers
as a hand on a clock. All the inspection operations do is advance that hand
along the clock. While the tests check to see if the hand lands in a particular
spot (a multiple of a particular number) on that clock. In mathematical terms:

        x | y iff x mod y = 0

Since we are operating on a clock, we can reset (take the modulo) the worry
levels when we pass the *edge* of the clock. The only question is, how big does
our clock need to be?

Let's pretend that we are only concerned with testing wether or not our worry
level is divisible by 3. Evidently, our clock needs to have at least three
positions. But it can also have more, 3 is just the lowest possible. If we also
want to test if our worry level is divisible by 2, how large does our clock
need to be now? It turns out that it has to be 2*3 or larger. The same pattern
holds if we want to test for more possible divisors. Proving why this is, is
left as an exercise to the reader :)
"""
from typing import Callable
from functools import reduce


class Monkey:
    def __init__(
            self,
            items: list[int],                     # list of worry levels
            operation: Callable[[int], int],      # inspection operation
            worry_op: Callable[[int], int],       # worry decrease operation
            test: Callable[[int], bool],          # test operation
            true_monkey: int,               # monkey index to throw to if true
            false_monkey: int               # monkey index to throw to if false
    ):
        self.items = items
        self.operation = operation
        self.worry_op = worry_op
        self.inspection_count = 0
        self.test = test
        self.true_monkey = true_monkey
        self.false_monkey = false_monkey

    def throw(self) -> int:
        """Return the foremost item and remove it from this monkey's item list.
        """
        return self.items.pop(0)

    def catch(self, item) -> None:
        """Append the provided item to this monkey's item list."""
        self.items.append(item)

    def inspect(self) -> int:
        """Inspect an item and return the index to the monkey which this monkey
        whises to throw its item to next.
        """
        self.inspection_count += 1

        # Do inspeciton operation on item
        self.items[0] = self.operation(self.items[0])

        # Do worry decrease operation on item
        self.items[0] = self.worry_op(self.items[0])

        # Return which monkey we want to throw the item to
        if self.test(self.items[0]):
            return self.true_monkey

        return self.false_monkey

    @property
    def has_items(self) -> bool:
        return bool(self.items)

    def __str__(self):
        return str(self.items).strip('[]')


def get_items(itemline: str) -> list[int]:
    """Parse an item line as found it the input beginnig with: 'Starting
    items:', and return a list of items represented by their worry levels.
    """
    return [int(item.rstrip(',')) for item in itemline.split()[2:]]


def get_operation(opline: str) -> Callable[[int], int]:
    """Parse an operation line as found in the input beginnig with:
    'Operation:', and return a callable performing said operation.
    """
    opexpr = opline.split()[3:]
    if ' '.join(opexpr) == 'old * old':
        return lambda n: n**2

    if ' '.join(opexpr) == 'old + old':
        return lambda n: n*2

    if ' '.join(opexpr[0:2]) == 'old *':
        return lambda n: n * int(opexpr[-1])

    if ' '.join(opexpr[0:2]) == 'old +':
        return lambda n: n + int(opexpr[-1])

    raise ValueError('get_operation could not match operation expression!')


def get_test(testline: str) -> Callable[[int], bool]:
    """Parse a test line as found in the input beginning with: 'Test:', and
    return a callable performing said test.
    """
    contents = testline.split()
    if ' '.join(contents[1:3]) == 'divisible by':
        return lambda n: n % int(contents[-1]) == 0

    raise ValueError('get_test could not match test expression!')


def get_target_monkeys(destlines: list[str]) -> tuple[int, int]:
    """Parse destination lines as found in the input beginning with: 'If true:'
    and 'If false:' and return indicies representing target monkeys for item
    throws.
    """
    return int(destlines[0].split()[-1]), int(destlines[1].split()[-1])


def get_monkeys(
        worry_op: Callable[[int], int],
        puzzle_input: str = 'input.txt'
) -> list[Monkey]:
    """Parse the input at puzzle_input and return a list of Monkeys."""
    monkeys = []
    with open(puzzle_input) as f:
        line = f.readline()
        while line:
            lines = []
            while line and line != '\n':
                lines.append(line)
                line = f.readline()

            # Create new monkey
            items = get_items(lines[1])
            operation = get_operation(lines[2])
            test = get_test(lines[3])
            target = get_target_monkeys(lines[4:])
            monkeys.append(
                Monkey(items, operation, worry_op, test, target[0], target[1])
            )

            line = f.readline()

    return monkeys


def get_divisors(puzzle_input: str = 'input.txt') -> list[int]:
    """Parse the puzzle input and return a list of divisors used for the tests.
    """
    divisors = []
    with open(puzzle_input) as f:
        line = f.readline()
        while line:
            if line != '\n' and line.split()[0] == "Test:":
                divisors.append(int(line.split()[-1]))
            line = f.readline()

    return divisors


def do_rounds(n: int, monkeys: list[Monkey]) -> None:
    """Perform n rounds of monkey stuff-slinging simian shenanigans!"""
    for _ in range(n):
        for monkey in monkeys:
            while monkey.has_items:
                target_monkey = monkey.inspect()
                monkeys[target_monkey].catch(monkey.throw())


def print_monkeys(monkeys: list[Monkey], print_items=False) -> None:
    sorted_monkeys = sorted(
        monkeys,
        key=lambda monkey: monkey.inspection_count,
        reverse=True
    )
    for monkey in sorted_monkeys:
        print(f'Monkey {monkeys.index(monkey)}:')
        print(f'   Inspections: {str(monkey.inspection_count)}')
        if print_items:
            print(f'   Items: {str(monkey)}')


def print_monkeys_business(monkeys: list[Monkey]) -> None:
    sorted_monkeys = sorted(
        monkeys,
        key=lambda monkey: monkey.inspection_count,
        reverse=True
    )
    monkey_business = (
        sorted_monkeys[0].inspection_count *
        sorted_monkeys[1].inspection_count
    )
    print(f'Monkey business level: {monkey_business}')


if __name__ == '__main__':
    # Part 1
    monkeys = get_monkeys(lambda n: n // 3)
    do_rounds(20, monkeys)
    print('For part 1 we have:')
    print_monkeys(monkeys)
    print_monkeys_business(monkeys)

    print('\nFor part 2 we have:')
    clock_size = reduce(lambda x, y: x * y, get_divisors())
    monkeys = get_monkeys(lambda n: n % clock_size)
    do_rounds(10000,  monkeys)
    print_monkeys(monkeys)
    print_monkeys_business(monkeys)
