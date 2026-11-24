import math
from typing import Callable, Optional, Tuple
from game import Game, MAX, State
import time


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
    
class AlphaBetaSearcher:
    def __init__(
        self,
        game: Game,
        eval_fn: Callable[[Game, State], float] = zero_eval,
        ordering: str = "center",
    ):
        self.game = game
        self.eval_fn = eval_fn
        self.ordering = ordering
        self.nodes = 0
        self.pruned = 0

    def _order_actions(self, state: State, actions: list[int]) -> list[int]:
        """Hamleleri seçilen stratejiye göre sıralar: natural, center veya heuristic."""
        if self.ordering == "natural":
            return list(actions)

        center = (self.game.C - 1) / 2.0
        if self.ordering == "center":
            return sorted(actions, key=lambda c: (abs(c - center), c))

        if self.ordering == "heuristic":
            def score(action: int) -> tuple[float, float, int]:
                nxt = self.game.result(state, action)
                if self.game.is_terminal(nxt):
                    val = float(self.game.utility(nxt))
                else:
                    val = self.eval_fn(self.game, nxt)
                # MAX yüksek değeri, MIN düşük değeri önce dener
                primary = -val if state.player == MAX else val
                return (primary, abs(action - center), action)

            return sorted(actions, key=score)

        raise ValueError(f"Bilinmeyen sıralama stratejisi: {self.ordering}")

    def max_value(self, state: State, depth: int, alpha: float, beta: float) -> float:
        self.nodes += 1
        if self.game.is_terminal(state):
            return float(self.game.utility(state))
        if depth == 0:
            return self.eval_fn(self.game, state)

        v = -math.inf
        actions = self._order_actions(state, self.game.actions(state))
        for i, a in enumerate(actions):
            v = max(v, self.min_value(self.game.result(state, a), depth - 1, alpha, beta))
            if v >= beta:
                self.pruned += len(actions) - i - 1
                return v
            alpha = max(alpha, v)
        return v

    def min_value(self, state: State, depth: int, alpha: float, beta: float) -> float:
        self.nodes += 1
        if self.game.is_terminal(state):
            return float(self.game.utility(state))
        if depth == 0:
            return self.eval_fn(self.game, state)

        v = math.inf
        actions = self._order_actions(state, self.game.actions(state))
        for i, a in enumerate(actions):
            v = min(v, self.max_value(self.game.result(state, a), depth - 1, alpha, beta))
            if v <= alpha:
                self.pruned += len(actions) - i - 1
                return v
            beta = min(beta, v)
        return v

    def choose_move(self, state: State, depth: int) -> Tuple[Optional[int], float]:
        """Kökte alpha-beta budaması ile en iyi hamleyi ve değerini döndürür."""
        self.nodes = 0
        self.pruned = 0
        actions = self._order_actions(state, self.game.actions(state))
        if not actions:
            return None, float(self.game.utility(state))

        best_move = actions[0]
        alpha, beta = -math.inf, math.inf

        if state.player == MAX:
            best_val = -math.inf
            for a in actions:
                val = self.min_value(self.game.result(state, a), depth - 1, alpha, beta)
                if val > best_val:
                    best_val = val
                    best_move = a
                alpha = max(alpha, best_val)
        else:
            best_val = math.inf
            for a in actions:
                val = self.max_value(self.game.result(state, a), depth - 1, alpha, beta)
                if val < best_val:
                    best_val = val
                    best_move = a
                beta = min(beta, best_val)

        return best_move, best_val

    def effective_branching_factor(self, depth: int) -> float:
        """Etkin dallanma çarpanı: (düğüm_sayısı) ** (1 / derinlik)."""
        if depth <= 0 or self.nodes <= 0:
            return 0.0
        return self.nodes ** (1.0 / depth)
    
class SearchTimeout(Exception):
    """Belirlenen zaman sınırı dolduğunda aramayı güvenli şekilde keser."""
    pass


class IterativeDeepeningSearcher:
    def __init__(
        self,
        game: Game,
        eval_fn: Callable[[Game, State], float] = zero_eval,
        ordering: str = "heuristic",
    ):
        self.game = game
        self.eval_fn = eval_fn
        self.ordering = ordering
        self.nodes = 0
        self.pruned = 0
        self.completed_depth = 0
        self.last_elapsed = 0.0

    def _order_actions(
        self, state: State, actions: list[int], pv_move: Optional[int] = None
    ) -> list[int]:
        center = (self.game.C - 1) / 2.0

        if self.ordering == "natural":
            ordered = list(actions)
        elif self.ordering == "center":
            ordered = sorted(actions, key=lambda c: (abs(c - center), c))
        else:
            def score(action: int) -> tuple[float, float, int]:
                nxt = self.game.result(state, action)
                val = float(self.game.utility(nxt)) if self.game.is_terminal(nxt) else self.eval_fn(self.game, nxt)
                primary = -val if state.player == MAX else val
                return (primary, abs(action - center), action)

            ordered = sorted(actions, key=score)

        # Önceki derinliğin en iyi hamlesini (PV) en başa al
        if pv_move is not None and pv_move in ordered:
            ordered.remove(pv_move)
            ordered.insert(0, pv_move)

        return ordered

    def _check_time(self, deadline: float) -> None:
        if (self.nodes & 127) == 0 and time.perf_counter() >= deadline:
            raise SearchTimeout()

    def _max_value(
        self, state: State, depth: int, alpha: float, beta: float, deadline: float
    ) -> float:
        self.nodes += 1
        self._check_time(deadline)

        if self.game.is_terminal(state):
            return float(self.game.utility(state))
        if depth == 0:
            return self.eval_fn(self.game, state)

        v = -math.inf
        actions = self._order_actions(state, self.game.actions(state))
        for i, a in enumerate(actions):
            v = max(v, self._min_value(self.game.result(state, a), depth - 1, alpha, beta, deadline))
            if v >= beta:
                self.pruned += len(actions) - i - 1
                return v
            alpha = max(alpha, v)
        return v

    def _min_value(
        self, state: State, depth: int, alpha: float, beta: float, deadline: float
    ) -> float:
        self.nodes += 1
        self._check_time(deadline)

        if self.game.is_terminal(state):
            return float(self.game.utility(state))
        if depth == 0:
            return self.eval_fn(self.game, state)

        v = math.inf
        actions = self._order_actions(state, self.game.actions(state))
        for i, a in enumerate(actions):
            v = min(v, self._max_value(self.game.result(state, a), depth - 1, alpha, beta, deadline))
            if v <= alpha:
                self.pruned += len(actions) - i - 1
                return v
            beta = min(beta, v)
        return v

    def choose_move(
        self, state: State, time_limit: float = 0.5, max_depth: int = 12
    ) -> Tuple[Optional[int], float]:
        """Zaman sınırı içinde derinliği 1'den başlayarak artırır."""
        start = time.perf_counter()
        deadline = start + time_limit

        self.nodes = 0
        self.pruned = 0
        self.completed_depth = 0

        legal = self.game.actions(state)
        if not legal:
            self.last_elapsed = time.perf_counter() - start
            return None, float(self.game.utility(state))

        # Süre çok kısaysa bile geçerli bir hamle döndürmek için başlangıç değeri
        best_move = self._order_actions(state, legal)[0]
        best_val = 0.0

        for depth in range(1, max_depth + 1):
            try:
                actions = self._order_actions(state, legal, pv_move=best_move)
                alpha, beta = -math.inf, math.inf
                curr_move = actions[0]

                if state.player == MAX:
                    curr_val = -math.inf
                    for a in actions:
                        val = self._min_value(self.game.result(state, a), depth - 1, alpha, beta, deadline)
                        if val > curr_val:
                            curr_val = val
                            curr_move = a
                        alpha = max(alpha, curr_val)
                else:
                    curr_val = math.inf
                    for a in actions:
                        val = self._max_value(self.game.result(state, a), depth - 1, alpha, beta, deadline)
                        if val < curr_val:
                            curr_val = val
                            curr_move = a
                        beta = min(beta, curr_val)

                # Derinlik başarıyla tamamlandıysa sonucu güncelle
                best_move = curr_move
                best_val = curr_val
                self.completed_depth = depth

                # Kesin kazanma bulunduysa daha derine inmeye gerek yok
                if (state.player == MAX and best_val == 1.0) or (state.player == MIN and best_val == -1.0):
                    break

            except SearchTimeout:
                break

        self.last_elapsed = time.perf_counter() - start
        return best_move, best_val