from PyQt6.QtWidgets import QInputDialog

from trivia_game.game_gui import GameGUI
from trivia_game.game_engine import GameEngine, TriviaQuestion


class TriviaGame():
    """Trivia Game, which is the combination of the game engine and the GUI."""
    def __init__(
        self,
        logging_level_str,
        question_category_column_name,
        data_info,
        data_path,
    ):
        # Create a game
        self.game_engine = GameEngine(logging_level_str=logging_level_str)
        self.n_total_questions = self.game_engine.set_game_parameters(
            question_category_column_name=question_category_column_name,
            data_info=data_info,
            data_path=data_path,
        )
        self.is_game_over: bool = False
        # Create a GUI
        self.gui = GameGUI()

        # Assign GUI to the GameEngine function calls
        self._connect_buttons()

        # Init a question number counter
        self.current_question = TriviaQuestion()
        self.question_counter = 0

        self.seed = -1

    def start_game(self):
        """Start the trivia game."""
        self.gui.show()

    def _connect_buttons(self):
        """Assign buttons of GUI to the functionality of the game."""
        self.gui.start_button.clicked.connect(self._click_start_game)
        self.gui.next_question_button.clicked.connect(self._show_next_question)
        self.gui.show_answer_button.clicked.connect(self._show_answer)
        self.gui.goto_question_button.clicked.connect(self._go_to_question)

    def _click_start_game(self):
        self.seed, ok = QInputDialog.getInt(self.gui, "Enter the game seed", "Game Seed:")
        if ok:
            self._start_game_with_seed(self.seed)

    def _show_next_question(self):
        self.current_question = self._get_next_question()
        if self.is_game_over:
            self.gui.show_question("Game is over, thanks for playing!")
            self.gui.show_question_options([])
        else:
            self.gui.display_next_question(
                trivia_question=self.current_question,
                question_number_txt=self._return_question_number_txt()
            )

    def _show_answer(self):
        if self.is_game_over:
            answer_text = "Thanks for playing, the game is over!"
        else:
            answer_text = self.current_question.get_answer_text()
        self.gui.show_answer(answer_text)

    def _go_to_question(self):
        """Goes to the desired question by replaying the game with the same seed"""
        question_number, ok = QInputDialog.getInt(
            self.gui,
            "Enter the question to go to", f"Question, max is {self.n_total_questions}:"
        )
        if ok:
            # Replay the game until that question number with the same seed (Hacky solution)
            self._start_game_with_seed(self.seed)
            for i in range(question_number):
                self.current_question = self._get_next_question()

            self.gui.display_next_question(
                trivia_question=self.current_question,
                question_number_txt=self._return_question_number_txt()
            )

    def _get_next_question(self) -> TriviaQuestion:
        """Get a question from the game engine."""
        current_question = self.game_engine.get_next_question()
        if current_question.is_question_valid():
            self.question_counter += 1
            self.is_game_over = False
        else:
            self.is_game_over = True
        return current_question

    def _start_game_with_seed(self, seed: int):
        """Reset state."""
        self.question_counter = 0
        self.current_question = TriviaQuestion()
        self.game_engine.initialize_game(seed=seed)
        self.gui.update_after_start_game(seed_num=seed)

    def _return_question_number_txt(self) -> str:
        return f"{self.question_counter}/{self.n_total_questions}"
