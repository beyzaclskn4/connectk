from typing import Iterator, List
from game import Game, MAX, MIN, State
import math

# Tek bir K-uzunluklu penceredeki taş sayısına göre temel ağırlıklar
WINDOW_WEIGHTS = {
    1: 1.0,
    2: 5.0,
    3: 25.0,
    4: 150.0,
}


def _iter_windows(game: Game, state: State) -> Iterator[List[int]]:
    """Tahtadaki tüm geçerli K-uzunluklu pencereleri (V=1 silindir dahil) üretir."""
    R, C, K = game.R, game.C, game.K
    board = state.board

    # 1. Dikey pencereler (sarma yok)
    for r in range(R - K + 1):
        for c in range(C):
            yield [board[r + i][c] for i in range(K)]

    # 2. Yatay pencereler (V=1 ise kenardan sarar)
    c_limit = C if game.V == 1 else (C - K + 1)
    for r in range(R):
        for c in range(c_limit):
            yield [board[r][(c + i) % C] for i in range(K)]

    # 3. Sağ-aşağı çapraz pencereler (\)
    for r in range(R - K + 1):
        for c in range(c_limit):
            yield [board[r + i][(c + i) % C] for i in range(K)]

    # 4. Sol-aşağı çapraz pencereler (/)
    if game.V == 1:
        for r in range(R - K + 1):
            for c in range(C):
                yield [board[r + i][(c - i) % C] for i in range(K)]
    else:
        for r in range(R - K + 1):
            for c in range(K - 1, C):
                yield [board[r + i][c - i] for i in range(K)]


def score_window(window: List[int]) -> float:
    """
    Tek bir pencereyi MAX açısından puanlar.
    Hem MAX hem MIN taşı varsa pencere kilitlidir (0 puan).
    """
    max_count = window.count(MAX)
    min_count = window.count(MIN)

    if max_count > 0 and min_count > 0:
        return 0.0
    if max_count > 0:
        return WINDOW_WEIGHTS.get(max_count, 500.0)
    if min_count > 0:
        return -WINDOW_WEIGHTS.get(min_count, 500.0)
    return 0.0

def center_control_score(game: Game, state: State) -> float:
    """Merkez sütuna yakın taşlar için küçük pozisyonel bonus hesaplar."""
    center = (game.C - 1) / 2.0
    score = 0.0
    for r in range(game.R):
        for c in range(game.C):
            cell = state.board[r][c]
            if cell == 0:
                continue
            # Merkezde en yüksek, kenarlara gittikçe azalan ağırlık
            weight = max(0.0, (center + 1.0) - abs(c - center))
            if cell == MAX:
                score += weight
            elif cell == MIN:
                score -= weight
    return score


def evaluate(game: Game, state: State) -> float:
    """
    Durumu MAX açısından (-1.0, +1.0) aralığında değerlendirir.
    Terminal durumlarda doğrudan kesin fayda (-1, 0, +1) döndürür.
    """
    if game.is_terminal(state):
        return float(game.utility(state))

    raw_score = 0.0
    for window in _iter_windows(game, state):
        raw_score += score_window(window)

    raw_score += center_control_score(game, state)

    # Misère (V=2) varyantında taş dizmek dezavantajdır
    if game.V == 2:
        raw_score = -raw_score

    # Terminal değerleri (±1.0) asla aşmamak için (-0.95, +0.95) aralığına sıkıştır
    return 0.95 * math.tanh(raw_score / 250.0)