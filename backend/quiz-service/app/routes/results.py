from flask import Blueprint, request, jsonify, g, current_app
from marshmallow import ValidationError
from bson import json_util
import json
from app.schemas.quiz_schema import QuizSubmissionSchema
from app.services.result_processor import ResultProcessor
from app.utils.auth_helper import token_required

results_bp = Blueprint('results', __name__)

quiz_submission_schema = QuizSubmissionSchema()


def serialize_result(result):
    return json.loads(json_util.dumps(result))


@results_bp.route('/submit', methods=['POST'])
@token_required
def submit_quiz():
    try:
        data = quiz_submission_schema.load(request.get_json())
        quiz_id = request.args.get('quiz_id')

        if not quiz_id:
            return jsonify({"error": "quiz_id parameter required"}), 400

        quiz = current_app.quiz_model.find_quiz_by_id(quiz_id)
        if not quiz:
            return jsonify({"error": "Quiz not found"}), 404

        if g.user_role == 'PLAYER' and quiz.get('status') != 'APPROVED':
            return jsonify({"error": "Quiz is not available for players"}), 403

        duration_seconds = quiz.get('duration_seconds')
        if isinstance(duration_seconds, int) and data['time_spent_seconds'] > duration_seconds:
            return jsonify({"error": "Quiz time limit exceeded"}), 400

        result = ResultProcessor.submit_quiz_async(
            quiz_id=quiz_id,
            user_id=g.user_id,
            user_first_name=getattr(g, 'user_first_name', ''),
            user_last_name=getattr(g, 'user_last_name', ''),
            submitted_answers=data['answers'],
            time_spent_seconds=data['time_spent_seconds']
        )

        return jsonify(result), 202  

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        return jsonify({"error": "Failed to submit quiz"}), 500


@results_bp.route('/my-results', methods=['GET'])
@token_required
def get_my_results():
    try:
        results = ResultProcessor.get_user_results(g.user_id)
        return jsonify({
            "results": [serialize_result(r) for r in results]
        }), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve results"}), 500


@results_bp.route('/leaderboard/<quiz_id>', methods=['GET'])
@token_required
def get_leaderboard(quiz_id):
    try:
        limit = request.args.get('limit', 10, type=int)
        auth_token = request.headers.get('Authorization', '')
        leaderboard = ResultProcessor.get_quiz_leaderboard(quiz_id, limit, auth_token)

        return jsonify({
            "leaderboard": [serialize_result(r) for r in leaderboard]
        }), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve leaderboard"}), 500

