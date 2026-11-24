import unittest
from game import Game, MAX, MIN
from search import MinimaxSearcher, AlphaBetaSearcher, IterativeDeepeningSearcher
from evaluate import evaluate


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

class TestStage4IterativeDeepening(unittest.TestCase):
    def setUp(self):
        self.game = Game(R=5, C=7, K=5, V=1, seed=30)

    def test_respects_time_limit_and_returns_legal_move(self):
        """Kısa zaman sınırında bile süreyi aşmadan yasal bir hamle döndürmeli."""
        id_searcher = IterativeDeepeningSearcher(self.game, eval_fn=evaluate, use_tt=True)
        s = self.game.state_from_moves([3, 3, 4, 4])
        move, _ = id_searcher.choose_move(s, time_limit=0.15, max_depth=10)

        self.assertIn(move, self.game.actions(s))
        self.assertGreaterEqual(id_searcher.completed_depth, 1)
        self.assertLess(id_searcher.last_elapsed, 0.35)

    def test_tt_matches_alpha_beta_and_reduces_nodes(self):
        """TT açıkken sabit derinlikte Alpha-Beta ile aynı değeri üretmeli ve TT hit almalı."""
        s = self.game.state_from_moves([3, 3, 4, 4])
        ab = AlphaBetaSearcher(self.game, eval_fn=evaluate, ordering="heuristic")
        _, ab_val = ab.choose_move(s, depth=4)

        id_tt = IterativeDeepeningSearcher(self.game, eval_fn=evaluate, ordering="heuristic", use_tt=True)
        _, tt_val = id_tt.choose_move(s, time_limit=5.0, max_depth=4)

        self.assertAlmostEqual(ab_val, tt_val, places=6)
        self.assertEqual(id_tt.completed_depth, 4)
        self.assertGreater(id_tt.tt_hits, 0)

    def test_finds_immediate_win_early(self):
        """Tek hamlede kazanma varken derinlik 1'de durup doğru hamleyi seçmeli."""
        s = self.game.state_from_moves([0, 1, 0, 1, 0, 1, 0, 2])
        id_searcher = IterativeDeepeningSearcher(self.game, eval_fn=evaluate, use_tt=True)
        move, val = id_searcher.choose_move(s, time_limit=1.0, max_depth=8)

        self.assertEqual(move, 0)
        self.assertEqual(val, 1.0)
        self.assertEqual(id_searcher.completed_depth, 1)
if __name__ == "__main__":
    unittest.main()