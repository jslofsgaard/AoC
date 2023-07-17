import functools
from enum import Enum
from itertools import chain, zip_longest


class Decision(Enum):
    IN_ORDER = True
    OUT_OF_ORDER = False
    INCONCLUSIVE = None


Packet = list | int | None


def parse_input(path="input.txt") -> list[tuple[Packet, Packet]]:
    res = []

    def parse_pair(fp) -> tuple[str, str]:
        left = fp.readline()
        right = fp.readline()
        if left and right:
            res.append((eval(left), eval(right)))

        return left, right

    with open(path, "r") as fp:
        left, right = parse_pair(fp)
        while left and right:
            fp.readline()  # discard empty seperator line
            left, right = parse_pair(fp)

    return res


class InconclusiveComparisonError(Exception):
    pass


def compare(left: Packet, right: Packet) -> bool:
    def inner_compare(left: Packet, right: Packet) -> Decision:
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
            return inner_compare([left], right)
        elif isinstance(left, list) and isinstance(right, int):
            return inner_compare(left, [right])

        # At this point, both left and right are lists
        for inner_left, inner_right in zip_longest(left, right, fillvalue=None):
            retval = inner_compare(inner_left, inner_right)
            if retval != Decision.INCONCLUSIVE:
                return retval

        return Decision.INCONCLUSIVE

    result = inner_compare(left, right)
    if result == Decision.INCONCLUSIVE:
        raise InconclusiveComparisonError()

    return result.value


@functools.total_ordering
class PacketData:
    def __init__(self, data):
        self.data = data

    def __lt__(self, other) -> bool:
        return compare(self.data, other.data)

    def __eq__(self, other) -> bool:
        try:
            compare(self.data, other.data)
            return False
        except InconclusiveComparisonError:
            return True

    def __repr__(self) -> None:
        return f"PacketData({self.data})"


if __name__ == "__main__":
    # Part 1
    packet_pairs = parse_input()
    indexed_pairs = enumerate((compare(*pair) for pair in packet_pairs), start=1)
    sum_indicies = sum(elem[0] for elem in indexed_pairs if elem[1] is True)
    print(f"Sum of ordered packet indexation: {sum_indicies}")

    # Part 2
    dividers = [PacketData([[2]]), PacketData([[6]])]
    packet_data = sorted(
        list(map(PacketData, chain.from_iterable(packet_pairs))) + dividers
    )
    p1, p2 = packet_data.index(dividers[0]), packet_data.index(dividers[1])
    print(f"Decoder key: {(p1+1)*(p2+1)}")
