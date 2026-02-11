import random

def shuffle_options(question):
    if hasattr(question, "options") and question.options:
        random.shuffle(question.options)
    return question

def shuffle_quiz_options(quiz):
    for question in quiz.questions:
        question = shuffle_options(question)
    return quiz
    