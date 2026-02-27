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
    