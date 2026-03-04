import random

def shuffle_option(question):
    """
    Xáo trộn field options.
    """
    if hasattr(question, "options") and question.options:
        random.shuffle(question.options)
    return question


def shuffle_quiz_options(quiz):
    """
    Xáo trộn thứ tự đáp án của mỗi câu hỏi trong quiz để đảm bảo tính ngẫu nhiên.
    """
    for question in quiz.questions:
        question = shuffle_option(question)
    return quiz


def shuffle_quiz_options_all(quiz):
    """
    Xáo trộn thứ tự đáp án của tất cả câu hỏi trong quiz.
    Hàm này xử lý cả choice-based questions và fill-in-the-blank questions.
    
    :param quiz: GenerateQuizResponse - Quiz object chứa danh sách questions
    :return: GenerateQuizResponse - Quiz với options đã được shuffle
    """
    for question in quiz.questions:
        # Chỉ shuffle cho choice-based questions (SINGLE_CHOICE, MULTIPLE_CHOICE, TRUE_FALSE)
        # Không shuffle cho FILL_IN_THE_BLANK vì thứ tự blank_number phải giữ nguyên
        if question.question_type != "FILL_IN_THE_BLANK":
            shuffle_option(question)
    return quiz