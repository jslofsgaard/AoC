from typing import Union, List


class CalorieList:
    def __init__(self, calories: List[int]):
        self.calories = calories

    @property
    def total(self):
        return sum(self.calories)


def parse_line(line: str) -> Union[int, None]:
    """Read a line and return an integer if the line can be converted
    to it, None otherwise.
    """
    try:
        return int(line)
    except ValueError:
        return None


def get_calorie_lists(puzzle_input: str = 'input.txt') -> List[CalorieList]:
    """Construct a list of CalorieLists from the input located at puzzle_input.
    """
    with open(puzzle_input) as f:
        items = []
        line = f.readline()
        while line:
            calories = []
            calorie = parse_line(line)
            while calorie:
                calories.append(calorie)
                calorie = parse_line(f.readline())

            items.append(CalorieList(calories))
            line = f.readline()

        return items


if __name__ == '__main__':
    calorie_lists = sorted(
            get_calorie_lists(),
            key=lambda calorie_list: calorie_list.total,
            reverse=True
    )
    top_three_total = sum(map(
            lambda calorie_list: calorie_list.total,
            calorie_lists[0:3]
    ))

    print(f'Max: {calorie_lists[0].total}')
    print(
        'Top three: '
        f'{calorie_lists[0].total}, '
        f'{calorie_lists[1].total}, '
        f'{calorie_lists[2].total}'
    )
    print(f'Top three total: {top_three_total}')
