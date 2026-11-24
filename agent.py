from typing import Optional
from game import Game, State
from search import IterativeDeepeningSearcher
from evaluate import evaluate


class Agent:
    """Connect-K varyantı için zaman sınırlı, TT destekli ana oyun ajanı."""

    def __init__(
        self,
        game: Game,
        time_limit: float = 0.5,
        max_depth: int = 12,
        ordering: str = "heuristic",
        use_tt: bool = True,
    ):
        self.game = game
        self.time_limit = time_limit
        self.max_depth = max_depth
        self.searcher = IterativeDeepeningSearcher(
            game=game,
            eval_fn=evaluate,
            ordering=ordering,
            use_tt=use_tt,
        )
        self.last_value: float = 0.0
        self.last_depth: int = 0
        self.last_nodes: int = 0
        self.last_elapsed: float = 0.0

    def choose_move(
        self, state: State, time_limit: Optional[float] = None
    ) -> Optional[int]:
        """Verilen durum için zaman sınırı içinde en iyi yasal hamleyi döndürür."""
        limit = self.time_limit if time_limit is None else time_limit
        move, val = self.searcher.choose_move(
            state, time_limit=limit, max_depth=self.max_depth
        )
        self.last_value = val
        self.last_depth = self.searcher.completed_depth
        self.last_nodes = self.searcher.nodes
        self.last_elapsed = self.searcher.last_elapsed
        return move


if __name__ == "__main__":
    g = Game(R=5, C=7, K=5, V=1, seed=30)
    agent = Agent(g, time_limit=0.3)
    s = g.initial_state()
    mv = agent.choose_move(s)
    print(
        f"Secilen hamle: {mv} | skor={agent.last_value:+.3f} | "
        f"derinlik={agent.last_depth} | dugum={agent.last_nodes} | "
        f"sure={agent.last_elapsed:.3f}s"
    )