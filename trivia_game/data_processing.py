from typing import Tuple, List
import random

import pandas as pd

from trivia_game.game_logger import create_logger


def _generate_random_int_and_sort(n):
    """Generate numbers 1:N and sort randomly."""
    integers = list(range(1, n + 1))
    # Shuffle the integers
    random.shuffle(integers)
    # Sort the elements and get the sorted indices
    sorted_indices = sorted(range(len(integers)), key=lambda k: integers[k])
    return integers, sorted_indices


class QuestionCategoryData:
    """The interface class between the game engine and the game data for a specified question
    category.
    """
    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        question_column_title: str,
        answer_column_title: str,
        question_option_columns_list: List[str],
        logging_level_str: str = "none"
    ):
        self.logger = create_logger(name=name, logging_level_str=logging_level_str)
        self.df = df
        self.name = name
        self.num_questions = len(df)
        self.question_column_title = question_column_title
        self.answer_column_title = answer_column_title
        self.question_option_columns_list = question_option_columns_list
        # Append question_val and is_question_asked column to dataframe self.df
        self.df['Question Value'] = [0.0 for _ in range(self.num_questions)]
        self.df['Sorting Indices'] = [-1 for _ in range(self.num_questions)]
        self.df['is_question_asked'] = [False for _ in range(self.num_questions)]

        self.reset_game_state()
        self.next_question_idx = 0
        self.logger.info("Initialized " + __class__.__name__ + ": " + name)
        self.logger.debug("Number of questions = " + str(self.num_questions))

    def reset_game_state(self):
        """ Resets game state, which is tracked by columns of self.df"""
        self.df['is_question_asked'] = [False for _ in range(self.num_questions)]
        self.df['Question Value'], self.df['Sorting Indices'] = self._sort_questions_randomly()
        self.next_question_idx = 0
        self.logger.debug('Game Reset: Questions are re-shuffled')

    def get_next_question(self):
        """Retrive the next question from the dataframe and update  'is_question_asked' column.

        Also returns a boolean flag to indicate whether an unasked question is returned from
        the dataframe.
        """
        msk_next_question = self.df['Sorting Indices'] == self.next_question_idx
        next_question = self.df[self.df['Sorting Indices'] == self.next_question_idx]
        n_questions_retrieved = len(next_question)
        if n_questions_retrieved > 1:
            raise ValueError("More than 1 question is retrieved, check get_next_question() method.")
        elif len(next_question) == 1:
            # An unasked question is succesfully retrieved from the dataframe.
            self.next_question_idx += 1
            is_query_valid = True
            self.df.loc[msk_next_question, 'is_question_asked'] = True
        else:
            # The dataframe has no unasked questions.
            is_query_valid = False
        return next_question, is_query_valid

    def get_num_of_remaining_questions(self):
        """Return the number of unasked questions."""
        return (~self.df['is_question_asked']).values.sum()  # False.sum()

    def _sort_questions_randomly(self):
        """Sort the questions randomly.

        Sorting is done by re-setting 'Question Value' and 'Sorting Indices' columns
        """
        random_elements, sorted_indices = _generate_random_int_and_sort(self.num_questions)
        self.logger.debug(f'Sorted {self.num_questions} questions.')
        assert (len(random_elements) == len(sorted_indices))
        assert (len(random_elements) == len(self.df['Question Value']))
        return random_elements, sorted_indices


class DataLoader:
    """ Class to Load & Parse the Excel database."""
    def __init__(self, question_category_column_name, data_info, logging_level_str):
        self.logging_level_str = logging_level_str
        # Store State Data
        self.question_category_column_name = question_category_column_name
        self.data_info = data_info
        self.logger = create_logger(name="DataLoader", logging_level_str=logging_level_str)
        self.logger.info("Initialized DataLoader.")

    def parse_excel_data(self, database_path: pd.DataFrame) -> list[QuestionCategoryData]:
        """ Parse the Excel file for each question category defined in self.data_info.keys().

        For each question category, a QuestionCategoryData object is created which interfaces with
        the main game engine.
        """
        self.logger.debug("Reading question/ answer data from " + database_path + ".")
        question_categories = list(self.data_info.keys())
        # Read excel sheet and treat data as strings
        # Replace NaN values with ""
        df = pd.read_excel(
            database_path,
            dtype=str,
        )
        df = df.fillna("")
        self.logger.debug("Parsing question categories:")
        self.logger.debug(question_categories)
        question_category_db_list = [
            self._parse_by_question_category(df, question_category)
            for question_category in question_categories
        ]
        return question_category_db_list

    def _parse_by_question_category(
        self,
        df: pd.DataFrame,
        question_category: str
    ) -> QuestionCategoryData:
        """ Parse the dataframe for the given question category(type)."""
        # Return the rows matching the specified question category
        matching_rows_indices = self._get_rows_by_question_category(
            self.question_category_column_name,
            df,
            question_category
        )
        # Return the columns to extract for the specified question category
        (question_column_title,
         answer_column_title,
         question_option_columns_list) = self._get_columns_by_question_category(
            data_info_dict=self.data_info,
            question_category=question_category
        )
        self.logger.debug(f"Question category defined: {question_category}")
        self.logger.debug(f"Question columm: {question_column_title}")
        self.logger.debug(f"Answer column: {answer_column_title}")
        self.logger.debug(f"Question optional text columns(): {question_option_columns_list}")

        # Create QuestionCategoryData object which is a wrapper class around pandas.Dataframe
        subset_df = df.loc[
            matching_rows_indices,
            [question_column_title, answer_column_title] + question_option_columns_list
        ]
        return QuestionCategoryData(
            name=question_category,
            df=subset_df,
            question_column_title=question_column_title,
            answer_column_title=answer_column_title,
            question_option_columns_list=question_option_columns_list,
            logging_level_str=self.logging_level_str
        )

    @staticmethod
    def _get_rows_by_question_category(
        question_category_column_name: str,
        df: pd.DataFrame,
        question_category: str
    ) -> List:
        """
        Find the rows where the specific question category is stored

        Leading and ending whitespaces are removed from strings while doing the comparison.
        """
        matching_rows_indices = df.index[
            df[question_category_column_name].str.strip() == question_category.strip()
        ].tolist()
        return matching_rows_indices

    @staticmethod
    def _get_columns_by_question_category(
        data_info_dict: dict[str:dict],
        question_category: str
    ) -> Tuple[str, str, List[str]]:
        # question_category is a key of data_info_dict dictionary
        # each key of question_category must hold a dictionary with the keys below:
        # 'Question_column', Question_option_columns and 'Answer_column'
        question_category_dict = data_info_dict[question_category]

        question_column_title = question_category_dict['Question_column']
        answer_column_title = question_category_dict['Answer_column']
        question_option_columns_list = question_category_dict['Question_option_columns']

        return question_column_title, answer_column_title, question_option_columns_list
