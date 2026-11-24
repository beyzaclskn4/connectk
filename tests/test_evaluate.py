import unittest
from game import Game, MAX, MIN
from evaluate import evaluate


class TestStage3Evaluate(unittest.TestCase):
    def setUp(self):
        self.game = Game(R=5, C=7, K=5, V=1, seed=30)

    def test_empty_board_is_zero(self):
        """Boş tahtada değerlendirme tam 0.0 olmalı."""
        s = self.game.initial_state()
        self.assertAlmostEqual(evaluate(self.game, s), 0.0, places=6)

    def test_bounds_strictly_inside_terminal_values(self):
        """Terminal olmayan durumlarda skor (-1.0, +1.0) aralığında kalmalı."""
        # MAX için çok güçlü tehdit (4 taş üst üste, henüz terminal değil)
        s = self.game.state_from_moves([0, 1, 0, 1, 0, 1, 0, 2])
        val = evaluate(self.game, s)
        self.assertGreater(val, 0.0)
        self.assertLess(val, 1.0)

    def test_symmetry_max_vs_min(self):
        """Aynı tahta dizilimi MAX ve MIN arasında ters işaretli olmalı."""
        # MAX sütun 3'te, MIN sütun 0'da -> merkez avantajı MAX lehine
        s1 = self.game.state_from_moves([3, 0])
        # Tam tersi: MAX sütun 0'da, MIN sütun 3'te -> merkez avantajı MIN lehine
        s2 = self.game.state_from_moves([0, 3])
        self.assertAlmostEqual(evaluate(self.game, s1), -evaluate(self.game, s2), places=6)

    def test_cylinder_wrap_around_threat(self):
        """Silindir modunda kenardan saran 4'lü tehdit yüksek pozitif skor vermeli."""
        # Sütun 5, 6, 0, 1'de MAX taşları (silindir sarma ile 4'lü tehdit)
        s = self.game.state_from_moves([5, 3, 6, 3, 0, 3, 1, 2])
        val = evaluate(self.game, s)
        self.assertGreater(val, 0.3)
        self.assertLess(val, 1.0)

    def test_terminal_state_returns_exact_utility(self):
        """Kazanma durumunda doğrudan +1.0 dönmeli."""
        s = self.game.state_from_moves([0, 1, 0, 1, 0, 1, 0, 2, 0])
        self.assertEqual(evaluate(self.game, s), 1.0)


if __name__ == "__main__":
    unittest.main()