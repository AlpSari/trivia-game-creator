"""Contains the functions that is used to convert the user input to the required data format."""
import json


def parse_game_metadata_from_json(game_metadata_path: str) -> tuple[str, dict]:
    """Parse the JSON file explaining the Excel file format to create the trivia game metadata.

        JSON file is read as a nested dictionary, with the following structure:
        1) The top level dictionary must contain only a single key,
        corresponding to the name of the column in Excel file,
        which stores the question categories.
        2) This top level key stores a dictionary,
        where each key is the name of the 'question category' and the value is another dictionary
        with 3 keys, storing the relevant column names for that 'question category'.
        3) Those 3 keys are (case-insensitive): "question", "answer", "additional text".
            - The value stored in the "question" key is
            the column name in the Excel file storing the
            question strings for that 'question category'.
            - The value stored in the "answer" key is
            the column name in the Excel file storing the
            answer strings for that 'question category'.
            - The "additional text" key is optional, and is
            the column name in the Excel file storing the
            extra question strings for that 'question category'.
            This flexibility might be needed for some custom question types,
            such as a Multiple-Choice question type, where one would not only show the question,
            but also the choices, where one of which is the right answer.
    """
    with open(game_metadata_path, 'r', encoding='utf-8') as file:
        json_content = file.read()
    data = json.loads(json_content)

    # 1) There must be a single top level key
    keys_top_level = list(data.keys())
    n_keys = len(keys_top_level)
    if n_keys != 1:
        raise ValueError(
            f"Input JSON file must contain only 1 key (now -> {n_keys}) in the top level, "
            "corresponding to the column name where question categories are stored!"
        )
    question_category_column_name = keys_top_level[0]
    game_metadata = dict()
    # Each key is assumed to be a question category
    for question_category, question_category_data in data[question_category_column_name].items():
        # For each question category, there must exist "question" and "answer" (case-insensitive)
        # keys, "additional text" key is extra
        dict_with_lowercase_keys = _convert_dict_keys_to_lowercase(question_category_data)
        additional_columns_list = dict_with_lowercase_keys.get("additional text", [])
        if not additional_columns_list:
            print(
                "'additional text' key is not found, or is empty"
                f" for question category = {question_category}"
            )
        game_metadata[question_category] = _create_qa_dict(
            question_column_name=dict_with_lowercase_keys["question"],
            answer_column_name=dict_with_lowercase_keys["answer"],
            question_extra_text_columns=additional_columns_list,
        )
    return question_category_column_name, game_metadata


def _create_qa_dict(
    question_column_name: str,
    answer_column_name: str,
    question_extra_text_columns: list[str]
) -> dict:
    """Help create metadata for the trivia game dataloader"""
    return {
        'Question_column': question_column_name,
        'Answer_column': answer_column_name,
        'Question_option_columns': question_extra_text_columns,
    }


def _convert_dict_keys_to_lowercase(input_dict: dict):
    """Convert keys to lowercase."""
    return {k.lower(): v for k, v in input_dict.items()}
