from bson import ObjectId
from flask import current_app
from datetime import datetime


class QuizService:
    @staticmethod
    def create_quiz(quiz_data, author_id, author_email=None):
        quiz_model = current_app.quiz_model

        quiz_data['author_id'] = author_id
        quiz_data['author_email'] = author_email or 'unknown@mail.com'
        quiz_data['status'] = 'PENDING'

        for question in quiz_data.get('questions', []):
            question['_id'] = ObjectId()
            for answer in question.get('answers', []):
                answer['_id'] = ObjectId()

        quiz_id = quiz_model.create_quiz(quiz_data)
        quiz = quiz_model.find_quiz_by_id(quiz_id)

        return quiz

    @staticmethod
    def get_quiz(quiz_id):
        quiz_model = current_app.quiz_model
        quiz = quiz_model.find_quiz_by_id(quiz_id)

        if not quiz:
            raise ValueError("Quiz not found")

        return quiz

    @staticmethod
    def list_quizzes(status=None, author_id=None):
        quiz_model = current_app.quiz_model

        filter_dict = {}
        if status:
            filter_dict['status'] = status
        if author_id:
            filter_dict['author_id'] = author_id

        quizzes = quiz_model.find_all_quizzes(filter_dict)
        return quizzes

    @staticmethod
    def get_quizzes_by_author(author_id):
        quiz_model = current_app.quiz_model
        quizzes = quiz_model.find_all_quizzes({'author_id': author_id})
        return quizzes

    @staticmethod
    def update_quiz(quiz_id, update_data, user_id):
        quiz_model = current_app.quiz_model
        quiz = quiz_model.find_quiz_by_id(quiz_id)

        if not quiz:
            raise ValueError("Quiz not found")

        if quiz['status'] == 'APPROVED':
            raise ValueError("Cannot update approved quiz")

        if quiz['status'] == 'REJECTED':
            update_data['status'] = 'PENDING'
            update_data['rejection_reason'] = None
            update_data['rejected_by_admin_id'] = None

        success = quiz_model.update_quiz(quiz_id, update_data)
        if not success:
            raise ValueError("Failed to update quiz")

        return quiz_model.find_quiz_by_id(quiz_id)

    @staticmethod
    def delete_quiz(quiz_id, user_id):
        quiz_model = current_app.quiz_model
        quiz = quiz_model.find_quiz_by_id(quiz_id)

        if not quiz:
            raise ValueError("Quiz not found")

        success = quiz_model.delete_quiz(quiz_id)
        if not success:
            raise ValueError("Failed to delete quiz")

        return True

    @staticmethod
    def approve_quiz(quiz_id, admin_id, notes=None):
        quiz_model = current_app.quiz_model
        quiz = quiz_model.find_quiz_by_id(quiz_id)

        if not quiz:
            raise ValueError("Quiz not found")

        if quiz['status'] != 'PENDING':
            raise ValueError("Can only approve pending quizzes")

        success = quiz_model.approve_quiz(quiz_id, admin_id, notes)
        if not success:
            raise ValueError("Failed to approve quiz")

        return quiz_model.find_quiz_by_id(quiz_id)

    @staticmethod
    def reject_quiz(quiz_id, admin_id, reason):
        quiz_model = current_app.quiz_model
        quiz = quiz_model.find_quiz_by_id(quiz_id)

        if not quiz:
            raise ValueError("Quiz not found")

        if quiz['status'] != 'PENDING':
            raise ValueError("Can only reject pending quizzes")

        success = quiz_model.reject_quiz(quiz_id, admin_id, reason)
        if not success:
            raise ValueError("Failed to reject quiz")

        return quiz_model.find_quiz_by_id(quiz_id)
