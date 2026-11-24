import time
import unittest
from game import Game, MAX, MIN, perft


class TestStage0Game(unittest.TestCase):
    def setUp(self):
        # Senin varyantın: R=5, C=7, K=5, V=1 (Silindir), d=30
        self.game = Game(R=5, C=7, K=5, V=1, seed=30)

    def test_empty_board_perft(self):
        s = self.game.initial_state()
        for n in range(1, 5):
            self.assertEqual(perft(self.game, s, n), 7**n)

    def test_full_column_removed_from_actions(self):
        s = self.game.initial_state()
        for _ in range(5):  # R=5 olduğu için 5 taş sütunu doldurur
            s = self.game.result(s, 0)
        self.assertNotIn(0, self.game.actions(s))

    def test_vertical_win(self):
        # MAX sütun 0'a 5 taş dizer (aralara MIN sütun 1'e oynar)
        moves = [0, 1, 0, 1, 0, 1, 0, 1, 0]
        s = self.game.state_from_moves(moves)
        self.assertTrue(self.game.is_terminal(s))
        self.assertEqual(self.game.utility(s), 1)

    def test_horizontal_cylinder_wrap_win(self):
        # Silindir testi: sütun 5, 6, 0, 1, 2 yatayda 5'li yapar
        moves = [5, 3, 6, 3, 0, 3, 1, 3, 2]
        s = self.game.state_from_moves(moves)
        self.assertTrue(self.game.is_terminal(s))
        self.assertEqual(self.game.utility(s), 1)

    def test_diagonal_cylinder_wrap_win(self):
        # Silindir çapraz testi: (4,5), (3,6), (2,0), (1,1), (0,2)
        g = Game(R=5, C=7, K=5, V=1, seed=30)
        grid = [[0] * 7 for _ in range(5)]
        # MAX taşlarını çapraz (sarmalı) diz, son taşı (0,2) hamleyle bırakacağız
        for r, c in [(4, 5), (3, 6), (2, 0), (1, 1)]:
            grid[r][c] = MAX
        # (0,2)'ye düşebilmesi için altını MIN ile doldur
        for r in range(1, 5):
            grid[r][2] = MIN
        from game import State

        s = State(board=tuple(tuple(row) for row in grid), player=MAX)
        s = g.result(s, 2)
        self.assertTrue(g.is_terminal(s))
        self.assertEqual(g.utility(s), 1)

    def test_misere_variant(self):
        g = Game(R=5, C=7, K=4, V=2, seed=30)
        moves = [0, 1, 0, 1, 0, 1, 0]  # MAX 4'lü dizer ve kaybeder
        s = g.state_from_moves(moves)
        self.assertTrue(g.is_terminal(s))
        self.assertEqual(g.utility(s), -1)


if __name__ == "__main__":
    unittest.main()
