from io import TextIOWrapper
import sys

# Allows us to look recursively at a datastream that is 10000 characters long
sys.setrecursionlimit(10000)


def is_start_of_packet(data: str) -> bool:
    """Returns true if called with a string which has 4 or more unique
    characters in it.
    """
    return len(set(data)) >= 4


def get_marker_index(data: str, fd: TextIOWrapper) -> int:
    """Returns the number of chars processed in fd until a start-of-packet
    marker is found.
    """
    if is_start_of_packet(data[-4:]):
        return 0

    return 1 + get_marker_index(data + fd.read(1), fd)


def is_start_of_message(data: str) -> bool:
    """Returns true if called with a string which has 14 or more unique
    characters in it.
    """
    return len(set(data)) >= 14


def get_message_index(data: str, fd: TextIOWrapper) -> int:
    """Returns the number of chars processed in fd until a start-of-message
    marker is found.
    """
    if is_start_of_message(data[-14:]):
        return 0

    return 1 + get_message_index(data + fd.read(1), fd)


if __name__ == "__main__":
    with open("input.txt") as f:
        start_packet = get_marker_index("", f)
        f.seek(0)
        start_message = get_message_index("", f)
        print(f"The start of packet marker begins at: {start_packet}")
        print(f"The start of message marker begins at: {start_message}")
