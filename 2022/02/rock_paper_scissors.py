from __future__ import annotations
from typing import Union, Tuple, List, Callable


# Rock > Scissors
# Rock < Paper
# Rock = Rock

# Paper > Rock
# Paper < Scissors
# Paper = Paper

# Scissors > Paper
# Scissors < Rock
# Scissors = Scissors


class Hand:
    def __init__(self, value: str):
        if value in ("Rock", "Paper", "Scissor"):
            self.value = value
        else:
            raise ValueError

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        if not self == other:
            if self.value == "Rock":
                if other.value == "Paper":
                    return True
                else:
                    return False

            if self.value == "Paper":
                if other.value == "Scissor":
                    return True
                else:
                    return False

            if self.value == "Scissor":
                if other.value == "Rock":
                    return True
                else:
                    return False

        else:
            return False

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return self == other or self > other

    def clone(self) -> Hand:
        return Hand(self.value)

    def wins_to(self) -> Hand:
        if self.value == "Rock":
            return Hand("Scissor")

        elif self.value == "Paper":
            return Hand("Rock")

        else:
            return Hand("Paper")

    def losses_to(self) -> Hand:
        if self.value == "Rock":
            return Hand("Paper")

        elif self.value == "Paper":
            return Hand("Scissor")

        else:
            return Hand("Rock")


class Outcome:
    def __init__(self, value: str):
        if value in ("Loss", "Draw", "Win"):
            self.value = value
        else:
            raise ValueError

    def __invert__(self):
        if self.value == "Draw":
            return Outcome("Draw")

        elif self.value == "Win":
            return Outcome("Loss")

        else:
            return Outcome("Win")


class Game:
    def __init__(self, me: Hand, opponent: Hand):
        self.me = me
        self.opponent = opponent
        self.me.score, self.opponent.score = self.compute_score()

    def compute_score(self) -> Tuple[int]:
        scores = {
            "outcome": {"Loss": 0, "Draw": 3, "Win": 6},
            "shape": {"Rock": 1, "Paper": 2, "Scissor": 3},
        }

        if self.me == self.opponent:
            outcome = Outcome("Draw")
        elif self.me < self.opponent:
            outcome = Outcome("Loss")
        else:
            outcome = Outcome("Win")

        return (
            (scores["shape"][self.me.value] + scores["outcome"][outcome.value]),
            (
                scores["shape"][self.opponent.value]
                + scores["outcome"][(~outcome).value]
            ),
        )


def assumed_decrypt_line(line: str) -> Union[Game, None]:
    """Decrypt the line using the assumption that the right-hand side is my
    hand and return a game of rock, paper, scissors.
    """
    codes = {
        "opponent": {"A": "Rock", "B": "Paper", "C": "Scissor"},
        "me": {"X": "Rock", "Y": "Paper", "Z": "Scissor"},
    }
    try:
        return Game(Hand(codes["me"][line[2]]), Hand(codes["opponent"][line[0]]))
    except IndexError:
        return None


def explicit_decrypt_line(line: str) -> Union[Game, None]:
    """Decrypt the line using the elf's rule that the right-hand side is how
    the outcome of the game relative to me and hand and return a game of rock,
    paper, scissors.
    """

    def caluclate_my_hand(opponent_hand: Hand, my_outcome: Outcome) -> Hand:
        if my_outcome.value == "Draw":
            return opponent_hand.clone()
        elif my_outcome.value == "Win":
            return opponent_hand.losses_to()
        else:
            return opponent_hand.wins_to()

    codes = {
        "opponent": {"A": "Rock", "B": "Paper", "C": "Scissor"},
        "my_outcome": {"X": "Loss", "Y": "Draw", "Z": "Win"},
    }

    try:
        opponent_hand = Hand(codes["opponent"][line[0]])
        my_outcome = Outcome(codes["my_outcome"][line[2]])
        return Game(caluclate_my_hand(opponent_hand, my_outcome), opponent_hand)
    except IndexError:
        return None


def get_games(
    decrypt_line: Callable[str, Game], puzzle_input: str = "input.txt"
) -> List[Game]:
    """Using the provided decryption function construct a list of games from
    the input located at puzzle_input.
    """
    with open(puzzle_input) as f:
        games = []
        game = decrypt_line(f.readline())
        while game:
            games.append(game)
            game = decrypt_line(f.readline())

        return games


if __name__ == "__main__":
    games = get_games(assumed_decrypt_line)
    total_score = sum(game.me.score for game in games)
    print(f"Total score with assumption: {total_score}")

    games = get_games(explicit_decrypt_line)
    total_score = sum(game.me.score for game in games)
    print(f"Total score with explicit: {total_score}")
