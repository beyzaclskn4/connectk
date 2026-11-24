from dataclasses import dataclass
import random
from typing import List, Optional, Tuple

EMPTY = 0
MAX = 1
MIN = -1
BLOCKED = 2


@dataclass(frozen=True)
class State:
    board: Tuple[Tuple[int, ...], ...]  # R x C matris (0. satır en üst, R-1 en alt)
    player: int                         # Sıradaki oyuncu: MAX (1) veya MIN (-1)
    winner: Optional[int] = None        # Kazanan: MAX, MIN veya None
    last_move: Optional[Tuple[int, int]] = None  # Son taşın (satır, sütun) konumu
    move_count: int = 0


class Game:
    def __init__(self, R: int = 5, C: int = 7, K: int = 5, V: int = 1, seed: int = 30):
        self.R = R
        self.C = C
        self.K = K
        self.V = V
        self.seed = seed

    def initial_state(self) -> State:
        grid = [[EMPTY for _ in range(self.C)] for _ in range(self.R)]

        # V == 3 (Engelli): seed ile 2 farklı kalıcı engel yerleştir
        if self.V == 3:
            rng = random.Random(self.seed)
            obstacles = set()
            while len(obstacles) < 2:
                r = rng.randrange(self.R)
                c = rng.randrange(self.C)
                obstacles.add((r, c))
            for r, c in obstacles:
                grid[r][c] = BLOCKED

        board = tuple(tuple(row) for row in grid)
        return State(board=board, player=MAX, winner=None, last_move=None, move_count=0)

    def actions(self, state: State) -> List[int]:
        if state.winner is not None:
            return []
        # En üst hücre (satır 0) boşsa o sütuna taş düşebilir
        return [c for c in range(self.C) if state.board[0][c] == EMPTY]

    def result(self, state: State, col: int) -> State:
        if state.winner is not None:
            raise ValueError("Terminal durumdan hamle yapılamaz.")
        if col < 0 or col >= self.C or state.board[0][col] != EMPTY:
            raise ValueError(f"Yasa dışı hamle: sütun {col}")

        # Yerçekimi: yukarıdan aşağı in, ilk dolu/engelli hücrenin üstünde dur
        drop_row = 0
        for r in range(self.R):
            if state.board[r][col] == EMPTY:
                drop_row = r
            else:
                break

        # Yeni değişmez (immutable) tahta oluştur
        new_grid = [list(row) for row in state.board]
        new_grid[drop_row][col] = state.player
        new_board = tuple(tuple(row) for row in new_grid)

        # Kazanma kontrolü (sadece son konan taşın etrafında)
        winner = None
        if self._has_k_in_a_row(new_board, drop_row, col, state.player):
            # V == 2 (Misère): K taşı dizen kaybeder, diğer oyuncu kazanır
            winner = -state.player if self.V == 2 else state.player

        return State(
            board=new_board,
            player=-state.player,
            winner=winner,
            last_move=(drop_row, col),
            move_count=state.move_count + 1,
        )

    def _has_k_in_a_row(self, board: Tuple[Tuple[int, ...], ...], r: int, c: int, player: int) -> bool:
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for sign in (1, -1):
                nr, nc = r + sign * dr, c + sign * dc
                for _ in range(self.K - 1):
                    if self.V == 1:  # Silindir: yatayda başa sar
                        nc %= self.C
                    elif nc < 0 or nc >= self.C:
                        break
                    if nr < 0 or nr >= self.R:
                        break
                    if board[nr][nc] == player:
                        count += 1
                        if count >= self.K:
                            return True
                    else:
                        break
                    nr += sign * dr
                    nc += sign * dc
        return False

    def is_terminal(self, state: State) -> bool:
        return state.winner is not None or len(self.actions(state)) == 0

    def utility(self, state: State) -> int:
        if state.winner == MAX:
            return 1
        if state.winner == MIN:
            return -1
        return 0

    def state_from_moves(self, moves: List[int]) -> State:
        """Kontrol noktası formatındaki hamle dizisinden (örn: [3, 3, 4]) durum üretir."""
        s = self.initial_state()
        for col in moves:
            s = self.result(s, col)
        return s


def perft(game: Game, state: State, depth: int) -> int:
    if depth == 0 or game.is_terminal(state):
        return 1
    return sum(perft(game, game.result(state, a), depth - 1) for a in game.actions(state))