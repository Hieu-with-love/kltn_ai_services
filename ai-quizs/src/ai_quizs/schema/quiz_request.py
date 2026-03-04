from pydantic import BaseModel
from typing import List, Optional
from .quiz_common import QuizType, QuizDifficulty

class QuestionTypeConfig(BaseModel):
    """
    Cấu hình số lượng câu hỏi và độ khó cho một loại câu hỏi cụ thể.
    
    :param difficulty: Độ khó của câu hỏi (EASY, MEDIUM, HARD). Mặc định là EASY nếu không được cung cấp.
    :param number: Số lượng câu hỏi cần tạo cho loại câu hỏi này
    """
    difficulty: Optional[QuizDifficulty] = QuizDifficulty.EASY
    number: int

class QuizQuestionConfig(BaseModel):
    type: QuizType
    numberOfQuestions: List[QuestionTypeConfig]

class GenerateQuizRequest(BaseModel):

    """
    Request schema cho endpoint tạo quiz.
    
    :param context: Chủ đề hoặc nội dung mà quiz sẽ dựa trên. Có thể là chủ đề do giáo viên cung cấp hoặc nội dung đã được trích xuất và tóm tắt.
    :param questions: Danh sách cấu hình cho các loại câu hỏi và số lượng câu
    """
    context: str # Chủ đề do Teacher cung cấp or Nội dung đã extract + summary (Teacher có thể sửa)
    questions: List[QuizQuestionConfig] # Loại câu hỏi và số lượng câu hỏi cho mỗi loại