from functools import cache
from typing import Iterable

def parse_input(path="input.txt") -> list["Valve"]:
    valves = []
    with open(path, "r") as fp:
        line = fp.readline()
        while line:
            contents = line.split()
            location = contents[1]
            flow_rate = int(contents[4].partition('=')[-1][:-1])
            neighbours = [location.removesuffix(',') for location in contents[9:]]
            valves.append(Valve(location=location, flow_rate=flow_rate, neighbours=neighbours))
            line = fp.readline()

    return valves


class Valve:
    def __init__(self, location: str, flow_rate: int, neighbours: Iterable[str]):
        self.location = location
        self.flow_rate = flow_rate
        self.neighbours = tuple(neighbours)

    def __repr__(self) -> str:
        return f"Valve({self.location}, {self.flow_rate}, {self.neighbours})"


class TunnelNetworkError(Exception):
    pass


class TunnelNetwork:
    def __init__(self, valves: Iterable[Valve]):
        self.valves = tuple(valves)

    def __repr__(self) -> str:
        return f"TunnelNetwork({self.valves})"

    def by_location(self, location: str) -> Valve:
        assert len(self.valves) == len(set(valve.location for valve in self.valves))
        for valve in self.valves:
            if valve.location == location:
                return valve
        else:
            raise TunnelNetworkError(f"No valve having location: {location}")

    def optimal_release(self, total_time: int) -> int:

        @cache
        def descend(remaning_time: int, location: Valve, open_valves: tuple[Valve, ...]) -> int:
            assert remaning_time >= 0

            if remaning_time == 0:
                return 0

            options = []
            release = sum(valve.flow_rate for valve in open_valves)

            # Open the current valve
            if location not in open_valves and location.flow_rate > 0:
                options.append(release + descend(remaning_time - 1, location, open_valves + (location,)))

            # Move to a neighbour
            for other in location.neighbours:
                options.append(release + descend(remaning_time - 1, self.by_location(other), open_valves))

            return max(options, default=release)

        return descend(total_time, self.by_location("AA"), ())

        
if __name__ == "__main__":
    # Part 1
    network = TunnelNetwork(parse_input())
    optimal_release = network.optimal_release(30)
    print(f"The most pressure possible to release during 30 minuttes is: {optimal_release}")
