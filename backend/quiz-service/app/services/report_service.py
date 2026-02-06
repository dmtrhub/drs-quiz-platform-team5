from flask import current_app
from app.utils.pdf_generator import PDFGenerator
from bson import ObjectId
import os
import requests


class ReportService:

    @staticmethod
    def generate_quiz_report(quiz_id):
        """Generate a PDF report for a quiz with all results"""
        quiz_model = current_app.quiz_model
        result_model = current_app.result_model

        quiz = quiz_model.find_quiz_by_id(quiz_id)
        if not quiz:
            raise ValueError("Quiz not found")

        results = result_model.find_results_by_quiz(quiz_id)

        if not results:
            raise ValueError("No results found for this quiz")

        main_service_url = current_app.config.get('MAIN_SERVICE_URL', 'http://localhost:5000')
        for result in results:
            user_id = result.get('user_id')
            try:
                response = requests.get(f"{main_service_url}/users/{user_id}/public")
                if response.status_code == 200:
                    user_data = response.json().get('user', {})
                    first_name = user_data.get('first_name', '')
                    last_name = user_data.get('last_name', '')
                    result['user_name'] = f"{first_name} {last_name}".strip() or f"User {user_id}"
                else:
                    result['user_name'] = f"User {user_id}"
            except Exception as e:
                result['user_name'] = f"User {user_id}"

        pdf_buffer = PDFGenerator.generate_quiz_report(quiz, results)

        return pdf_buffer, quiz.get('title', 'quiz_report')

    @staticmethod
    def generate_user_report(result_id, user_info):
        """Generate a personalized PDF report for a user's quiz result"""
        result_model = current_app.result_model
        quiz_model = current_app.quiz_model

        result = result_model.find_result_by_id(result_id)
        if not result:
            raise ValueError("Result not found")

        quiz = quiz_model.find_quiz_by_id(str(result['quiz_id']))
        if not quiz:
            raise ValueError("Quiz not found")

        pdf_buffer = PDFGenerator.generate_user_result_report(quiz, result, user_info)

        return pdf_buffer, f"{quiz.get('title', 'quiz')}_result"
