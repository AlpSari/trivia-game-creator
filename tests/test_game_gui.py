"""Test Game GUI. Note that enabling these tests might lead to an unknown
Segmentation Fault error, which is not debugged yet."""
import sys
import unittest
from PyQt6.QtWidgets import QApplication
from trivia_game.game_gui import GameGUI


class TestGameGUI(unittest.TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)  # Create a QApplication instance
        self.gui = GameGUI()

    def tearDown(self):
        self.app.quit()  # Quit the application after each test

    def test_update_after_start_game(self):
        seed_num = 123
        self.gui.update_after_start_game(seed_num)
        self.assertTrue(self.gui.next_question_button.isEnabled())
        self.assertTrue(self.gui.show_answer_button.isEnabled())
        self.assertTrue(self.gui.goto_question_button.isEnabled())
        self.assertEqual(self.gui.user_input_label.text(), f"Seed: {seed_num}")
        self.assertFalse(self.gui.start_button.isVisible())
        self.assertFalse(self.gui.fix_answer_label.isHidden())


if __name__ == '__main__':
    unittest.main()
