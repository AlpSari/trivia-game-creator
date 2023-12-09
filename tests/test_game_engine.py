import unittest
import os
from unittest.mock import patch, Mock
from pandas import DataFrame
from trivia_game.game_engine import GameEngine, TriviaQuestion
from trivia_game.user_game_interface import parse_game_metadata_from_json


class TestTriviaQuestion(unittest.TestCase):
    def test_init_with_valid_question(self):
        data = DataFrame({'Question': ['Q1'], 'Answer': ['A1'], 'Option1': ['Opt1']})
        question = TriviaQuestion(
            is_question_valid=True,
            data=data,
            question_column_str='Question',
            answer_column_str='Answer',
            question_options_list=['Option1'],
            question_category='Category'
        )
        self.assertTrue(question.is_question_valid())
        self.assertEqual(question.get_question_text(), 'Q1')
        self.assertEqual(question.get_answer_text(), 'A1')
        self.assertEqual(question.get_question_category_text(), 'Category')
        self.assertEqual(question.get_question_options(), ['Opt1'])

    def test_init_with_invalid_question(self):
        question = TriviaQuestion()
        self.assertFalse(question.is_question_valid())
        self.assertEqual(question.get_question_text(), '')
        self.assertEqual(question.get_answer_text(), '')
        self.assertEqual(question.get_question_category_text(), '')
        self.assertEqual(question.get_question_options(), [])


class TestGameEngine(unittest.TestCase):
    @patch('trivia_game.data_processing.create_logger')
    def setUp(self, mock_create_logger):
        mock_logger = Mock()
        mock_create_logger.return_value = mock_logger
        self.game_engine = GameEngine(logging_level_str='none')

    def test_set_game_parameters(self):

        test_data_path = os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__))),
            "data/test_game_data.xlsx"
        )
        game_metadata_path = os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__))),
            "data/test_game_metadata.json"
        )
        question_category_column_name, game_metadata = parse_game_metadata_from_json(
            game_metadata_path
        )
        number_of_questions = self.game_engine.set_game_parameters(
            question_category_column_name, game_metadata, test_data_path
        )
        self.assertEqual(number_of_questions, 9)
        self.assertEqual(len(self.game_engine._ref_dict), 4)
        self.assertEqual(len(self.game_engine._question_categorys), 4)
