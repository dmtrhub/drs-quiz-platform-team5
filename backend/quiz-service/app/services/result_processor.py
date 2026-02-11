from multiprocessing import Process
from flask import current_app
from bson import ObjectId
from app.utils.scoring import calculate_quiz_score
import time

def process_quiz_result_async(quiz_id, user_id, submitted_answers, time_spent_seconds, app_config):
    """
    Async function to process quiz results in background
    This runs in a separate process
    """
    from pymongo import MongoClient
    from app.models.result import ResultModel
    from app.models.quiz import QuizModel

    mongo_client = MongoClient(app_config['MONGO_URI'])
    mongo_db = mongo_client[app_config['MONGO_DB']]

    quiz_model = QuizModel(mongo_db)
    result_model = ResultModel(mongo_db)

    print(f"[ResultProcessor] Processing result for quiz {quiz_id}, user {user_id}")

    try:
        quiz = quiz_model.find_quiz_by_id(quiz_id)
        if not quiz:
            print(f"[ResultProcessor] Quiz not found: {quiz_id}")
            return

        total_score, max_score, detailed_results = calculate_quiz_score(quiz, submitted_answers)

        rank = result_model.calculate_user_rank(quiz_id, total_score, time_spent_seconds)

        result_data = {
            'quiz_id': ObjectId(quiz_id),
            'quiz_title': quiz.get('title', 'Untitled Quiz'),
            'user_id': user_id,
            'score': total_score,
            'max_score': max_score,
            'time_spent_seconds': time_spent_seconds,
            'submitted_answers': detailed_results,
            'ranked_position': rank
        }

        result_id = result_model.create_result(result_data)

        print(f"[ResultProcessor] Result saved with ID: {result_id}, Score: {total_score}/{max_score}, Rank: {rank}")

        try:
            import requests
            main_service_url = app_config.get('MAIN_SERVICE_URL', 'http://localhost:5000')

            email_data = {
                'user_id': user_id,
                'quiz_title': quiz.get('title', 'Quiz'),
                'score': total_score,
                'max_score': max_score,
                'rank': rank
            }

            response = requests.post(
                f"{main_service_url}/api/notify/send-quiz-result-email",
                json=email_data
            )

            if response.status_code == 200:
                print(f"[ResultProcessor] Result email sent successfully to user {user_id}")
            else:
                print(f"[ResultProcessor] Failed to send result email: HTTP {response.status_code}")
        except Exception as email_error:
            print(f"[ResultProcessor] Error sending result email: {str(email_error)}")

    except Exception as e:
        print(f"[ResultProcessor] Error processing result: {str(e)}")
    finally:
        mongo_client.close()


class ResultProcessor:
    """Service to handle async quiz result processing"""

    @staticmethod
    def submit_quiz_async(quiz_id, user_id, submitted_answers, time_spent_seconds):
        """
        Submit quiz answers and process asynchronously
        Returns immediately while processing happens in background
        """
        app_config = {
            'MONGO_URI': current_app.config['MONGO_URI'],
            'MONGO_DB': current_app.config['MONGO_DB'],
            'MAIN_SERVICE_URL': current_app.config.get('MAIN_SERVICE_URL', 'http://localhost:5000')
        }

        process = Process(
            target=process_quiz_result_async,
            args=(quiz_id, user_id, submitted_answers, time_spent_seconds, app_config)
        )
        process.start()

        print(f"[ResultProcessor] Started async processing for quiz {quiz_id}, user {user_id}")

        return {
            'status': 'submitted',
            'message': 'Quiz submitted successfully. Results will be processed shortly.'
        }

    @staticmethod
    def get_user_results(user_id):
        """Get all results for a user"""
        result_model = current_app.result_model
        results = result_model.find_results_by_user(user_id)
        return results

    @staticmethod
    def get_quiz_leaderboard(quiz_id, limit=10, auth_token=''):
        """Get leaderboard for a quiz with user names"""
        import requests
        result_model = current_app.result_model
        leaderboard = result_model.get_leaderboard(quiz_id, limit)

        main_service_url = current_app.config.get('MAIN_SERVICE_URL', 'http://localhost:5000')

        headers = {}
        if auth_token:
            headers['Authorization'] = auth_token

        for entry in leaderboard:
            user_id = entry.get('user_id')
            try:
                response = requests.get(
                    f"{main_service_url}/users/{user_id}/public",
                    headers=headers
                )
                if response.status_code == 200:
                    user_data = response.json().get('user', {})
                    entry['user_name'] = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                    if not entry['user_name']:
                        entry['user_name'] = user_data.get('email', f'User {user_id}')
                else:
                    print(f"[Leaderboard] Failed to fetch user {user_id}: HTTP {response.status_code}")
                    entry['user_name'] = f'User {user_id}'
            except Exception as e:
                print(f"[Leaderboard] Failed to fetch user {user_id}: {str(e)}")
                entry['user_name'] = f'User {user_id}'

        return leaderboard
