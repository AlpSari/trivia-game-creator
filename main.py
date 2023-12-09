import sys
import os
import argparse
from PyQt6.QtWidgets import QApplication
from trivia_game.trivia_game import TriviaGame
from trivia_game.user_game_interface import parse_game_metadata_from_json


def main():
    parser = argparse.ArgumentParser(description='Trivia Game Argument Parser')
    parser.add_argument(
        '--questions-excel-path',
        dest='questions_excel_path',
        metavar='EXCEL_PATH',
        help='Path to the Excel(i.e. .xlsx extension) file containing game questions'
    )
    parser.add_argument(
        '--game-description-json-path',
        dest='game_description_json_path',
        metavar='JSON_PATH',
        help='Path to the JSON(i.e. .json extension) file containing game description'
    )
    parser.add_argument(
        '--launch-example-game',
        action='store_true',
        default=False,
        help='Launch the example game.'
    )
    parser.add_argument(
        '--logging-level',
        dest='logging_level',
        metavar='LOGGING_LEVEL_STRING',
        help='Logging level of the game, one of ["none", "info", "debug"]',
        default="none",
        choices=["none", "info", "debug"],
    )

    # Parse arguments
    args = parser.parse_args()
    logging_level = args.logging_level

    # --launch-example-game overrides the other options
    if args.launch_example_game:
        game_data_path = "example_game_data/example_game_questions.xlsx"
        game_definition_path = "example_game_data/example_game_definition.json"
    else:
        if args.questions_excel_path:
            game_data_path = args.questions_excel_path
        else:
            raise ValueError(
                "Excel file containing the questions is not specified. "
                "Either launch the example game with --launch-example-game flag "
                "or specify a path to the Excel file containing the questions either by "
                "--questions-excel-path argument.\n"
                "To get help about the arguments, run 'python main.py -h'."
            )
        if args.game_description_json_path:
            game_definition_path = args.game_description_json_path
        else:
            raise ValueError(
                "JSON file containing the game metadata is not specified. "
                "Either launch the example game with --launch-example-game flag or specify a path "
                "to the JSON file containing the questions either by --game-definition-path"
                " argument. \n"
                "To get help about the arguments, run 'python main.py -h'."
            )

    # Create absolute paths from input relative paths
    game_definition_path_absolute = _create_absolute_file_path(game_definition_path)
    game_data_path_absolute = _create_absolute_file_path(game_data_path)

    # Parse the given input JSON file
    (question_category_column_name, game_metadata) = parse_game_metadata_from_json(
        game_definition_path_absolute
    )
    # Start the game application
    sys.stdout.reconfigure(encoding='utf-8')
    app = QApplication(sys.argv)
    trivia_game = TriviaGame(
        logging_level_str=logging_level,
        question_category_column_name=question_category_column_name,
        data_info=game_metadata,
        data_path=game_data_path_absolute,
    )
    trivia_game.start_game()
    sys.exit(app.exec())


def _create_absolute_file_path(path_relative):
    """Given a path relative to the main.py, construct the absolute path."""
    directory_path = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.normpath(os.path.join(directory_path, path_relative))
    return absolute_path


if __name__ == '__main__':
    main()
