from enum import Enum
from itertools import zip_longest, starmap


class Decision(Enum):
    IN_ORDER = True
    OUT_OF_ORDER = False
    INCONCLUSIVE = None


Packet = list | int | None

def compare(left: Packet, right: Packet) -> Decision:
    if left is None:
        return Decision.IN_ORDER

    if left is not None and right is None:
        return Decision.OUT_OF_ORDER

    if isinstance(left, int) and isinstance(right, int):
        if left == right:
            return Decision.INCONCLUSIVE
        elif left < right:
            return Decision.IN_ORDER
        elif left > right:
            return Decision.OUT_OF_ORDER

    if isinstance(left, int) and isinstance(right, list):
        return compare([left], right)
    elif isinstance(left, list) and isinstance(right, int):
        return compare(left, [right])

    # At this point, both left and right are lists
    for inner_left, inner_right in zip_longest(left, right, fillvalue=None):
        retval = compare(inner_left, inner_right)
        if retval != Decision.INCONCLUSIVE:
            return retval

    return Decision.INCONCLUSIVE


def parse_input(path = 'input.txt') -> list[tuple[Packet, Packet]]:
    res = []

    def parse_pair(fp) -> tuple[str, str]:
        left = fp.readline()
        right = fp.readline()
        if left and right:
            res.append((eval(left), eval(right)))

        return left, right
    
    with open(path, 'r') as fp:
        left, right = parse_pair(fp)
        while left and right:
            fp.readline()  # discard empty seperator line
            left, right = parse_pair(fp)

    return res


def order(packets: list[tuple[Packet, Packet]]) -> list[tuple[int, Decision]]:
    return [
        (i+1, compare(*packets[i]))
        for i in range(len(packets))
    ]

if __name__ == '__main__':
    in_order = [elem for elem in order(parse_input()) if elem[1].value is True]
    print(f'The sum of the indices of the packets already in order is: {sum(elem[0] for elem in in_order)}')
