import math
from typing import Callable
from game import Game, State


def zero_eval(game: Game, state: State) -> float:
    """Aşama 1 için geçici değerlendirme fonksiyonu."""
    return 0.0


class MinimaxSearcher:
    def __init__(self, game: Game, eval_fn: Callable[[Game, State], float] = zero_eval):
        self.game = game
        self.eval_fn = eval_fn

    def max_value(self, state: State, depth: int) -> float:
        if self.game.is_terminal(state):
            return float(self.game.utility(state))
        if depth == 0:
            return self.eval_fn(self.game, state)

        v = -math.inf
        for a in self.game.actions(state):
            v = max(v, self.min_value(self.game.result(state, a), depth - 1))
        return v

    def min_value(self, state: State, depth: int) -> float:
        if self.game.is_terminal(state):
            return float(self.game.utility(state))
        if depth == 0:
            return self.eval_fn(self.game, state)

        v = math.inf
        for a in self.game.actions(state):
            v = min(v, self.max_value(self.game.result(state, a), depth - 1))
        return v