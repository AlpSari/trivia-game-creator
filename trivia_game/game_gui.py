from importlib.resources import path

from PyQt6 import uic
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from trivia_game.game_engine import TriviaQuestion


class GameGUI(QMainWindow):
    """Graphical User Interface of the trivia game."""
    def __init__(self):
        super().__init__()

        # Load the .ui file which defines the buttons, labels etc.
        package = __package__  # Get the current package name
        ui_path = path(package, "trivia_game.ui")
        uic.loadUi(ui_path, self)

        # Load the background images
        background_image_path = path(package, "background_img.png")
        pixmap = QPixmap(str(background_image_path))
        scaled_pixmap = pixmap.scaled(
            self.image_left.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_left.setPixmap(scaled_pixmap)
        self.image_mid.setPixmap(scaled_pixmap)
        self.image_right.setPixmap(scaled_pixmap)

        # Disable the buttons until the game starts.
        self.next_question_button.setEnabled(False)
        self.show_answer_button.setEnabled(False)
        self.goto_question_button.setEnabled(False)

        # Hide Answer Blocks until the game starts
        self.fix_answer_label.setHidden(True)

        # Add confirmation feature to the exit button
        self.exit_button.clicked.connect(self.show_exit_confirmation)

        # Qlabel list to show extra texts for the question
        # This is useful for question categories such as multiple question
        self.question_extra_labels = [
            self.question_extra_1,
            self.question_extra_2,
            self.question_extra_3,
            self.question_extra_4,
            self.question_extra_5,
        ]

        # Wrap the question according to the set box size,
        # This is needed when the question is too long.
        self.question_label.setWordWrap(True)
        self.question_label.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.Minimum
        )

    def display_next_question(self, trivia_question: TriviaQuestion, question_number_txt: str):
        """Display the given trivia question on the GUI."""

        # Clear the previous question before the next question is asked
        self._clear_previous_question()

        question_text = trivia_question.get_question_text()
        question_category = trivia_question.get_question_category_text()
        question_options = trivia_question.get_question_options()
        self.update_question_header(question_category, question_number_txt)
        self.show_question(question_text)
        self.show_question_options(question_options)

    def update_after_start_game(self, seed_num):
        """Enable the buttons and hide the start game button."""
        self.next_question_button.setEnabled(True)
        self.show_answer_button.setEnabled(True)
        self.goto_question_button.setEnabled(True)
        self.user_input_label.setText(f"Seed: {seed_num}")
        self.fix_answer_label.setHidden(False)
        self.start_button.hide()

    def show_answer(self, answer_text: str):
        """Display the given answer of the asked question."""
        self.fix_answer_label.setHidden(False)
        self.show_answer_label.setText(answer_text)

    def show_question(self, question_text: str):
        """Show the answer of the question."""
        self.question_label.setText(question_text)

    def _clear_previous_question(self):
        """Reset the QLabels set for the previous question ."""
        # Reset question
        self.show_question('')

        # Reset optional text shipped with the question
        for label_obj in self.question_extra_labels:
            label_obj.setText('')
            label_obj.setHidden(True)

        # Reset answer
        self.show_answer_label.setText('')

    def update_question_header(self, question_category_text: str, question_number_text: str):
        """Update the header above the asked questions."""
        self.q_category_label.setText(question_category_text)
        self.q_number_label.setText(question_number_text)

    def show_question_options(self, options_texts: list[str]):
        """Show additional text provided with the questions.

        Those additional texts will be shown using the QLabels stored in .question_extra_labels
        """
        n_options_input = len(options_texts)
        n_options_max = len(self.question_extra_labels)
        # First clear all the text
        for idx in range(n_options_max):
            self.question_extra_labels[idx].setHidden(False)
            self.question_extra_labels[idx].setText("")
        # Show the received text
        if n_options_input > len(self.question_extra_labels):
            err_msg_base = "More than maximum number of options is provided"
            err_msg_rest = f"Input = {n_options_input}, Maximum = {n_options_max}"
            raise ValueError(err_msg_base + err_msg_rest)

        for idx, option_text in enumerate(options_texts):
            self.question_extra_labels[idx].setHidden(False)
            self.question_extra_labels[idx].setText(option_text)

    def show_exit_confirmation(self):
        """Activate closeEvent."""
        self.close()

    def closeEvent(self, event):
        """Pop-up a box to confirm the exit."""
        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to exit the application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
