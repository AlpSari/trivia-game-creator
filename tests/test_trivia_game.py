# """Test Game Engine and GUI altogether. Note that enabling these tests might lead to an unknown
# Segmentation Fault error, which is not debugged yet."""
# import unittest
# import os
# from unittest.mock import MagicMock, patch
# from PyQt6.QtWidgets import QApplication
# from trivia_game.game_engine import GameEngine, TriviaQuestion
# from trivia_game.trivia_game import TriviaGame
# from trivia_game.user_game_interface import parse_game_metadata_from_json


# class TestTriviaGame(unittest.TestCase):
#     def setUp(self):
#         self.app = QApplication([])
#         self.game_engine = GameEngine(logging_level_str='info')
#         self.test_data_path = os.path.join(
#             os.path.abspath(os.path.join(os.path.dirname(__file__))),
#             "data/test_game_data.xlsx"
#         )
#         game_metadata_path = os.path.join(
#             os.path.abspath(os.path.join(os.path.dirname(__file__))),
#             "data/test_game_metadata.json"
#         )
#         question_category_column_name, game_metadata = parse_game_metadata_from_json(
#             game_metadata_path
#         )
#         self.trivia_game = TriviaGame(
#             logging_level_str='info',
#             question_category_column_name=question_category_column_name,
#             data_info=game_metadata,
#             data_path=self.test_data_path
#         )

#     def tearDown(self):
#         self.app.quit()

#     def test_start_game(self):
#         self.trivia_game.start_game()
#         self.assertTrue(self.trivia_game.gui.isVisible())

#     def test_click_start_game(self):
#         with patch('trivia_game.trivia_game.QInputDialog') as mock_input_dialog:
#             mock_input_dialog.getInt.return_value = (123, True)
#             self.trivia_game._start_game_with_seed = MagicMock()

#             self.trivia_game._click_start_game()

#             mock_input_dialog.getInt.assert_called_once()
#             self.trivia_game._start_game_with_seed.assert_called_once_with(123)

#     def test_start_game_with_seed(self):
#         self.trivia_game._start_game_with_seed(seed=123)
#         self.assertEqual(self.trivia_game.question_counter, 0)

#         def test_display_next_question(self):
#             with patch.object(self.trivia_game.gui, 'display_next_question') as \
#                     mock_display_next_question:
#                 # Ensures return value of game_engine.get_next_question is a TriviaQuestion with
#                 # is_question_valid  = True
#                 with patch.object(self.trivia_game.game_engine, 'get_next_question',
#                                   return_value=TriviaQuestion(is_question_valid=True)):
#                     self.trivia_game._display_next_question()

#                     mock_display_next_question.assert_called_once()
#                     # since we returned a valid question with our mock game engine, the counter is
#                     # incremented
#                     self.assertEqual(self.trivia_game.question_counter, 1)

#         def test_get_next_question(self):
#             with patch.object(self.game_engine, 'get_next_question',
#                               return_value=TriviaQuestion(is_question_valid=True)):
#                 next_question = self.trivia_game._get_next_question()
#                 self.assertIsInstance(next_question, TriviaQuestion)
#                 self.assertEqual(self.trivia_game.question_counter, 1)

#     def test_go_to_question(self):
#         with patch.object(self.gui, 'display_next_question'), \
#             patch.object(self.trivia_game, '_start_game_with_seed') as mock_start_game, \
#             patch.object(self.trivia_game, '_get_next_question',
#                          return_value=TriviaQuestion(is_question_valid=True)):
#             self.trivia_game.seed = 123
#             self.trivia_game.n_total_questions = 10
#             self.trivia_game._go_to_question()
#             mock_start_game.assert_called_once_with(123)

#     def test_show_answer(self):
#         # Mock the get_next_question method of self.game_engine
#         self.game_engine.get_next_question = MagicMock(
#             return_value=TriviaQuestion(is_question_valid=True)
#         )
#         # Mock the .show_answer method of self.gui
#         self.gui.show_answer = MagicMock()
#         self.trivia_game._display_next_question()
#         self.trivia_game._show_answer()
#         self.gui.show_answer.assert_called_once()
