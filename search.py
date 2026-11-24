import math
from typing import Callable, Optional, Tuple
from game import Game, MAX, State


def zero_eval(game: Game, state: State) -> float:
    """Aşama 1 için geçici değerlendirme fonksiyonu."""
    return 0.0


class MinimaxSearcher:
    def __init__(self, game: Game, eval_fn: Callable[[Game, State], float] = zero_eval):
        self.game = game
        self.eval_fn = eval_fn
        self.nodes = 0

    def _tie_break_order(self, actions: list[int]) -> list[int]:
        """Beraberlikte merkeze en yakın sütunu seçer."""
        center = (self.game.C - 1) / 2.0
        return sorted(actions, key=lambda c: (abs(c - center), c))

    def max_value(self, state: State, depth: int) -> float:
        self.nodes += 1
        if self.game.is_terminal(state):
            return float(self.game.utility(state))
        if depth == 0:
            return self.eval_fn(self.game, state)

        v = -math.inf
        for a in self.game.actions(state):
            v = max(v, self.min_value(self.game.result(state, a), depth - 1))
        return v

    def min_value(self, state: State, depth: int) -> float:
        self.nodes += 1
        if self.game.is_terminal(state):
            return float(self.game.utility(state))
        if depth == 0:
            return self.eval_fn(self.game, state)

        v = math.inf
        for a in self.game.actions(state):
            v = min(v, self.max_value(self.game.result(state, a), depth - 1))
        return v

    def choose_move(self, state: State, depth: int) -> Tuple[Optional[int], float]:
        """Kökte en iyi hamleyi ve değerini döndürür."""
        self.nodes = 0
        actions = self._tie_break_order(self.game.actions(state))
        if not actions:
            return None, float(self.game.utility(state))

        best_move = actions[0]
        if state.player == MAX:
            best_val = -math.inf
            for a in actions:
                val = self.min_value(self.game.result(state, a), depth - 1)
                if val > best_val:
                    best_val = val
                    best_move = a
        else:
            best_val = math.inf
            for a in actions:
                val = self.max_value(self.game.result(state, a), depth - 1)
                if val < best_val:
                    best_val = val
                    best_move = a

        return best_move, best_val

    def effective_branching_factor(self, depth: int) -> float:
        """Etkin dallanma çarpanı: (düğüm_sayısı) ** (1 / derinlik)."""
        if depth <= 0 or self.nodes <= 0:
            return 0.0
        return self.nodes ** (1.0 / depth)