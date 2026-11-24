import unittest
from game import Game, MAX, MIN
from search import MinimaxSearcher
from search import AlphaBetaSearcher

class TestStage1Minimax(unittest.TestCase):
    def setUp(self):
        # Senin varyantın: R=5, C=7, K=5, V=1 (Silindir), d=30
        self.game = Game(R=5, C=7, K=5, V=1, seed=30)
        self.searcher = MinimaxSearcher(self.game)

    def test_one_move_win_max(self):
        # MAX sütun 0'da 4 taş dizmiş, 5. taşla (sütun 0) hemen kazanmalı
        moves = [0, 1, 0, 1, 0, 1, 0, 2]
        s = self.game.state_from_moves(moves)
        move, val = self.searcher.choose_move(s, depth=2)
        self.assertEqual(move, 0)
        self.assertEqual(val, 1.0)

    def test_one_move_block_min(self):
        # MIN sütun 1'de 4 taş dizmiş; MAX sütun 1'e oynayıp engellemeli
        moves = [0, 1, 2, 1, 3, 1, 4, 1]
        s = self.game.state_from_moves(moves)
        move, val = self.searcher.choose_move(s, depth=2)
        self.assertEqual(move, 1)
        self.assertEqual(val, 0.0)

    def test_deterministic_choice_and_node_count(self):
        # Aynı konumda iki kez çalıştırılınca aynı hamleyi seçmeli[cite: 6]
        s = self.game.initial_state()
        m1, _ = self.searcher.choose_move(s, depth=2)
        nodes1 = self.searcher.nodes
        m2, _ = self.searcher.choose_move(s, depth=2)
        self.assertEqual(m1, m2)
        self.assertEqual(m1, 3)  # Boş tahtada merkez sütun (3)
        # Kök hariç max/min çağrıları: 7 + 49 = 56 düğüm
        self.assertEqual(nodes1, 56)


if __name__ == "__main__":
    unittest.main()