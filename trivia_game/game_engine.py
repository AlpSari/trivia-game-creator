import random
from typing import List

from pandas import DataFrame

from trivia_game.data_processing import DataLoader
from trivia_game.game_logger import create_logger


def _normalize_weight_list(weights: list) -> List:
    sum_weights = sum(weights)
    return [x / sum_weights if x != 0 else 0.0 for x in weights]


class TriviaQuestion():
    """Data interface between the GameEngine and the GUI."""
    def __init__(
        self,
        is_question_valid: bool = False,
        data: DataFrame = DataFrame(),
        question_column_str: str = "",
        answer_column_str: str = "",
        question_options_list: List[str] = [],
        question_category: str = "",
    ):
        self._is_question_valid = is_question_valid
        self._data = data if is_question_valid else DataFrame()
        self._question_column_str = question_column_str if is_question_valid else ""
        self._answer_column_str = answer_column_str if is_question_valid else ""
        self._question_options_list = question_options_list if is_question_valid else []
        self._question_category = question_category if is_question_valid else ""

    def __repr__(self):
        """Override for print() method calls"""
        if self._is_question_valid:
            return repr(self._data)
        else:
            return ""

    def get_question_text(self) -> str:
        """Return the question as a text."""
        return self._data[self._question_column_str].values[0] if self._is_question_valid else ""

    def get_answer_text(self) -> str:
        """Return the answer as a text."""
        return self._data[self._answer_column_str].values[0] if self._is_question_valid else ""

    def get_question_category_text(self) -> str:
        """Return the question category as a text."""
        return self._question_category if self._is_question_valid else ""

    def get_question_options(self) -> List[str]:
        """Return the question options as a list of strings."""
        return [
            self._data[column].values[0]
            for column in self._question_options_list
        ] if self._is_question_valid else []

    def is_question_valid(self) -> bool:
        """Return a boolean flag that indicates whether the question is valid."""
        return self._is_question_valid


class GameEngine:
    """Main class that controls the game."""
    def __init__(self, logging_level_str):
        self._logging_level_str = logging_level_str
        self._logging = create_logger(
            'GameEngine',
            logging_level_str=logging_level_str,
        )
        self._is_game_over = False
        self._ref_dict = dict()
        self._question_categorys = list()
        self._logging.info('Initialized GameEngine.')

    def set_game_parameters(
        self,
        question_category_column_name,
        data_info,
        data_path
    ) -> int:
        """Create a game with the specified data.

        Creates a dataloader with specified question categories.
        """
        dataloader = DataLoader(
            question_category_column_name=question_category_column_name,
            data_info=data_info,
            logging_level_str=self._logging_level_str,
        )

        # Sort questions into different categories and put them in a list
        question_category_list = dataloader.parse_excel_data(data_path)
        number_of_questions_total = sum(
            [category.num_questions for category in question_category_list]
        )

        # Store the question categories in a dictionary where keys are the names of categories
        self._ref_dict = {q_category.name: q_category for q_category in question_category_list}
        self._question_categorys = list(self._ref_dict.keys())

        self._logging.info('Data is loaded into the GameEngine succesfully.')
        return number_of_questions_total

    def initialize_game(self, seed=1):
        """ Initialize the game by randomly sorting questions by the given seed."""
        random.seed(seed)
        self._logging.debug(f'Initializing the game with seed = {seed}')

        for question_category in self._ref_dict.values():
            question_category.reset_game_state()
        self._is_game_over = False

    def get_next_question(self, weight_calculation_method='Weighted', weights_override=[]):
        """Get the next question to be asked.

        This is done by calculating the weights of each question category type and
        randomly selecting one using the normalizedd weights as probabilities.
        """
        if self._is_game_over:
            # Method called while the game is already over
            self._logging.debug('Game is over already!')
            return TriviaQuestion(is_question_valid=False)

        weights = self._calculate_weights_of_question_categories(weight_calculation_method)
        sum_weights = sum(weights)
        if sum_weights == 0:
            # Game is over
            self._logging.info('We are out of questions, game is over!')
            self._is_game_over = True
            return TriviaQuestion(is_question_valid=False)
        else:
            # Get Weights for Question Categories
            if len(weights_override) == 0:
                normalized_weights = _normalize_weight_list(weights)
            else:
                sum_weights_override = sum(weights_override)
                if sum_weights_override == 0:
                    normalized_weights = _normalize_weight_list(weights)
                    self._logging.debug(
                        "Weights override invalid! Fall back to default normalization."
                    )
                else:
                    normalized_weights = weights_override
                    self._logging.debug("Weights are overridden.")
            self._logging.debug(
                f"Probabilities for {self._question_categorys} categories are: {normalized_weights}"
            )

            # Choose the next question's category
            question_category = random.choices(
                self._question_categorys,
                weights=normalized_weights,
                k=1
            )[0]
            self._logging.debug(f'Selected Question Category is: {question_category}')
            question_category_database = self._ref_dict[question_category]

            # Return the next TriviaQuestion to be displayed.
            next_question_df, is_question_valid = question_category_database.get_next_question()
            question_column_str = question_category_database.question_column_title
            answer_column_str = question_category_database.answer_column_title
            question_options_list = question_category_database.question_option_columns_list

            columns_to_get = [question_column_str, answer_column_str] + question_options_list
            return TriviaQuestion(
                is_question_valid=is_question_valid,
                data=next_question_df.loc[:, columns_to_get],
                question_column_str=question_column_str,
                answer_column_str=answer_column_str,
                question_options_list=question_options_list,
                question_category=question_category)

    def _calculate_weights_of_question_categories(
        self,
        weight_calculation_method: str = 'Weighted'
    ) -> List[float]:
        """Return a weight value for each question category.

        For now, either equal weights are given to each category or
        the weights are the number of questions left for each category.
        """
        n_questions_left = [
            question_category.get_num_of_remaining_questions()
            for question_category in self._ref_dict.values()
        ]
        self._logging.debug(f'n_questions_left = {n_questions_left}')
        if weight_calculation_method != 'Weighted':
            # Assign equal weights, but if we are out of questions for a particular question
            # category, set the weight as 0 for that type
            weights = [
                1.0 if n_questions_left[i] != 0 else 0.0
                for i in range(len(n_questions_left))
            ]
        else:
            weights = n_questions_left
        return weights


if __name__ == "__main__":
    pass
