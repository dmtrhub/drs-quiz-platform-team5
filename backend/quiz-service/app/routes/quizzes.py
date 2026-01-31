from flask import Blueprint

quizzes_bp = Blueprint('quizzes', __name__)

from flask import Blueprint, request, jsonify

quizzes_bp = Blueprint('quizzes', __name__)


@quizzes_bp.route('/quizzes', methods=['GET'])
def list_quizzes():
    return jsonify({
        "message": "List quizzes placeholder",
        "quizzes": []
    }), 200


@quizzes_bp.route('/quizzes/<quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    return jsonify({
        "message": "Get quiz placeholder",
        "quiz_id": quiz_id
    }), 200


@quizzes_bp.route('/quizzes', methods=['POST'])
def create_quiz():
    data = request.get_json()
    return jsonify({
        "message": "Create quiz placeholder",
        "data": data
    }), 201
