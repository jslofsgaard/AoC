import math
from functools import cache
from itertools import chain, product
from typing import Iterable, Iterator


def parse_input(path="input.txt") -> list["Valve"]:
    valves = []
    with open(path, "r") as fp:
        line = fp.readline()
        while line:
            contents = line.split()
            location = contents[1]
            flow_rate = int(contents[4].partition("=")[-1][:-1])
            neighbours = [location.removesuffix(",") for location in contents[9:]]
            valves.append(
                Valve(location=location, flow_rate=flow_rate, neighbours=neighbours)
            )
            line = fp.readline()

    return valves


class Valve:
    def __init__(self, location: str, flow_rate: int, neighbours: Iterable[str]):
        self.location = location
        self.flow_rate = flow_rate
        self.neighbours = tuple(neighbours)

    def __repr__(self) -> str:
        return f"Valve({self.location}, {self.flow_rate}, {self.neighbours})"


# A path record is a mapping of valves to how long the valve was open for
PathRecord = dict[Valve, int]


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

    @property
    def start(self) -> Valve:
        return self.by_location("AA")

    @cache
    def dijkstra(
        self, start: Valve, target: Valve, *, steps: bool = False
    ) -> int | list[Valve]:
        nodes = {
            valve: {"distance": math.inf, "visited": False, "prior": None}
            for valve in self.valves
        }
        nodes[start]["distance"] = 0

        def unvisited_nodes():
            return (node for node in nodes if nodes[node]["visited"] == False)

        def unvisited_neighbours(node):
            return filter(
                lambda node: nodes[node]["visited"] == False,
                (self.by_location(location) for location in node.neighbours),
            )

        def closest_node(selection):
            return min(
                (node for node in selection), key=lambda node: nodes[node]["distance"]
            )

        while (
            nodes[target]["visited"] == False
            and nodes[closest_node(unvisited_nodes())]["distance"] != math.inf
        ):
            current = closest_node(unvisited_nodes())
            for neighbour in unvisited_neighbours(current):
                if nodes[neighbour]["distance"] > nodes[current]["distance"] + 1:
                    nodes[neighbour]["distance"] = nodes[current]["distance"] + 1
                    nodes[neighbour]["prior"] = current

            nodes[current]["visited"] = True

        if nodes[target]["visited"] == False:
            raise Exception(f"Unable to find a path from {start} to {target}")

        if not steps:
            return nodes[current]["distance"]

        def path(node):
            steps = []
            while node is not None:
                steps.append(node)
                node = nodes[node]["prior"]

            return reversed(steps)

        return list(path(current))

    @property
    def usefull_valves(self) -> Iterable[Valve]:
        return (valve for valve in self.valves if valve.flow_rate > 0)

    def paths(
        self, start: Valve, target: Valve, remaning_time: int, *, reached=()
    ) -> Iterator[PathRecord]:
        open_time = self.dijkstra(target, start) + 1
        if remaning_time <= open_time:
            return

        yield {target: remaning_time, start: remaning_time - open_time}

        visited = reached + (start,)
        potential_stops = [
            valve for valve in self.usefull_valves if valve not in visited
        ]
        time_to_open = {
            valve: self.dijkstra(valve, start) + 1 for valve in potential_stops
        }
        reachable_stops = (
            valve
            for valve in potential_stops
            if time_to_open[valve] + self.dijkstra(target, valve) <= remaning_time
        )
        for valve in reachable_stops:
            available_time = remaning_time - time_to_open[valve]
            for path_record in self.paths(
                valve,
                target,
                available_time,
                reached=visited,
            ):
                for item in path_record:
                    path_record[item] += time_to_open[valve]

                path_record[start] = path_record[valve] - time_to_open[valve]
                yield path_record


def score(path_record: PathRecord) -> int:
    return sum(valve.flow_rate * path_record[valve] for valve in path_record)


def aggregate(*path_records: PathRecord) -> PathRecord:
    accum = {}
    for precord in path_records:
        for valve in precord:
            if accum.get(valve, 0) < precord[valve]:
                accum[valve] = precord[valve]

    return accum


if __name__ == "__main__":
    # Part 1
    network = TunnelNetwork(parse_input())

    def precords(time):
        return chain.from_iterable(
            network.paths(valve, network.start, time)
            for valve in network.usefull_valves
        )

    optimal_release = max(score(precord) for precord in precords(30))
    print(
        f"The most pressure possible to release during 30 minutes is: {optimal_release}"
    )

    # Part 2
    most_efficient_1 = max(score(precord) for precord in precords(26))
    options_1 = [
        precord for precord in precords(26) if score(precord) == most_efficient_1
    ]
    optimal_release_2 = max(
        score(aggregate(*pair_precord))
        for pair_precord in product(options_1, precords(26))
    )
    print(
        f"The most pressure you and the elephant can release during 26 minutes is: {optimal_release_2}"
    )
