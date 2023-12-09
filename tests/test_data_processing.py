import unittest
from pandas import DataFrame
from trivia_game.data_processing import QuestionCategoryData, DataLoader


class TestQuestionCategoryData(unittest.TestCase):
    """Test uestionCategoryData functionality."""

    def setUp(self):
        self.mock_df = DataFrame({
            'Question': ['Q1', 'Q2', 'Q3'],
            'Answer': ['A1', 'A2', 'A3'],
            'Option1': ['Opt1', 'Opt2', 'Opt3']
        })
        self.mock_data_info = {
            'Category1': {
                'Question_column': 'Question',
                'Answer_column': 'Answer',
                'Question_option_columns': ['Option1']
            }
        }
        self.question_category = QuestionCategoryData(
            name='Category1',
            df=self.mock_df,
            question_column_title='Question',
            answer_column_title='Answer',
            question_option_columns_list=['Option1']
        )

    def test_get_next_question(self):
        next_question, is_valid = self.question_category.get_next_question()
        self.assertTrue(is_valid)
        self.assertTrue(next_question.iloc[0]['Question'] in self.mock_df['Question'].values)

    def test_get_num_of_remaining_questions(self):
        remaining = self.question_category.get_num_of_remaining_questions()
        self.assertEqual(remaining, 3)
        # Get a question, it should decrease the counter
        next_question, is_valid = self.question_category.get_next_question()
        remaining = self.question_category.get_num_of_remaining_questions()
        self.assertEqual(remaining, 2)

    def test_reset_game_state(self):
        self.question_category.reset_game_state()
        remaining = self.question_category.get_num_of_remaining_questions()
        self.assertEqual(remaining, 3)


class TestDataLoader(unittest.TestCase):
    """Test DataLoader functionality."""
    def test_parse_by_question_category(self):
        mock_df = DataFrame({
            'Category': ['Category1', 'Category1', 'Category2'],
            'Question': ['Q1', 'Q2', 'Q3'],
            'Answer': ['A1', 'A2', 'A3'],
            'Option1': ['Opt1', 'Opt2', 'Opt3']
        })
        data_loader = DataLoader(
            question_category_column_name='Category',
            data_info={'Category1': {'Question_column': 'Question',
                                     'Answer_column': 'Answer',
                                     'Question_option_columns': ['Option1']}},
            logging_level_str='none'
        )
        question_category = data_loader._parse_by_question_category(mock_df, 'Category1')
        self.assertIsInstance(question_category, QuestionCategoryData)
        self.assertEqual(question_category.name, 'Category1')
        self.assertEqual(question_category.num_questions, 2)


if __name__ == '__main__':
    unittest.main()
