from flask import Blueprint, request, jsonify

results_bp = Blueprint('results', __name__)


@results_bp.route('/results/submit', methods=['POST'])
def submit_results():
    data = request.get_json()
    return jsonify({
        "message": "Submit results placeholder",
        "data": data
    }), 200


@results_bp.route('/results/my-results', methods=['GET'])
def my_results():
    return jsonify({
        "message": "My results placeholder",
        "results": []
    }), 200


@results_bp.route('/results/leaderboard/<quiz_id>', methods=['GET'])
def leaderboard(quiz_id):
    return jsonify({
        "message": "Leaderboard placeholder",
        "quiz_id": quiz_id,
        "leaderboard": []
    }), 200
