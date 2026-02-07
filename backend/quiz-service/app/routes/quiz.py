from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError
from bson import ObjectId, json_util
import json
from app.schemas.quiz_schema import CreateQuizSchema, UpdateQuizSchema, ApprovalSchema, RejectionSchema
from app.services.quiz_service import QuizService
from app.services.notification_service import NotificationService
from app.utils.auth_helper import token_required, moderator_required, admin_required

quiz_bp = Blueprint('quiz', __name__)

create_quiz_schema = CreateQuizSchema()
update_quiz_schema = UpdateQuizSchema()
approval_schema = ApprovalSchema()
rejection_schema = RejectionSchema()


def serialize_quiz(quiz):
    return json.loads(json_util.dumps(quiz))


@quiz_bp.route('', methods=['POST'])
@moderator_required
def create_quiz():
    try:
        data = create_quiz_schema.load(request.get_json())

        quiz = QuizService.create_quiz(data, g.user_id, g.user_email)

        NotificationService.notify_quiz_created(serialize_quiz(quiz))

        return jsonify({
            "message": "Quiz created successfully and pending approval",
            "quiz": serialize_quiz(quiz)
        }), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to create quiz"}), 500


@quiz_bp.route('', methods=['GET'])
@token_required
def list_quizzes():
    try:
        if g.user_role in ['ADMIN', 'MODERATOR']:
            status = request.args.get('status')
            quizzes = QuizService.list_quizzes(status=status)
        else:
            quizzes = QuizService.list_quizzes(status='APPROVED')

        return jsonify({
            "quizzes": [serialize_quiz(q) for q in quizzes]
        }), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve quizzes"}), 500


@quiz_bp.route('/my-quizzes', methods=['GET'])
@moderator_required
def get_my_quizzes():
    try:
        quizzes = QuizService.get_quizzes_by_author(g.user_id)

        return jsonify({
            "quizzes": [serialize_quiz(q) for q in quizzes]
        }), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve your quizzes"}), 500


@quiz_bp.route('/pending', methods=['GET'])
@admin_required
def get_pending_quizzes():
    try:
        quizzes = QuizService.list_quizzes(status='PENDING')

        return jsonify({
            "quizzes": [serialize_quiz(q) for q in quizzes]
        }), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve pending quizzes"}), 500


@quiz_bp.route('/<quiz_id>', methods=['GET'])
@token_required
def get_quiz(quiz_id):
    try:
        quiz = QuizService.get_quiz(quiz_id)

        if g.user_role == 'PLAYER' and quiz['status'] != 'APPROVED':
            return jsonify({"error": "Quiz not available"}), 404

        return jsonify({"quiz": serialize_quiz(quiz)}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Failed to retrieve quiz"}), 500


@quiz_bp.route('/<quiz_id>', methods=['PUT'])
@moderator_required
def update_quiz(quiz_id):
    try:
        original_quiz = QuizService.get_quiz(quiz_id)
        was_rejected = original_quiz['status'] == 'REJECTED'

        data = update_quiz_schema.load(request.get_json())

        quiz = QuizService.update_quiz(quiz_id, data, g.user_id)

        if was_rejected and quiz['status'] == 'PENDING':
            NotificationService.notify_quiz_created(serialize_quiz(quiz))

        return jsonify({
            "message": "Quiz updated successfully",
            "quiz": serialize_quiz(quiz)
        }), 200

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to update quiz"}), 500


@quiz_bp.route('/<quiz_id>', methods=['DELETE'])
@moderator_required
def delete_quiz(quiz_id):
    try:
        quiz = QuizService.get_quiz(quiz_id)

        if g.user_role != 'ADMIN' and quiz['author_id'] != g.user_id:
            return jsonify({"error": "You can only delete your own quizzes"}), 403

        quiz_data = serialize_quiz(quiz)
        deleted_by_role = g.user_role

        QuizService.delete_quiz(quiz_id, g.user_id)

        NotificationService.notify_quiz_deleted(quiz_data, deleted_by_role)

        return jsonify({"message": "Quiz deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Failed to delete quiz"}), 500


@quiz_bp.route('/<quiz_id>/approve', methods=['PUT'])
@admin_required
def approve_quiz(quiz_id):
    try:
        data = approval_schema.load(request.get_json() or {})

        quiz = QuizService.approve_quiz(
            quiz_id,
            g.user_id,
            data.get('notes')
        )

        NotificationService.notify_quiz_approved(serialize_quiz(quiz), quiz['author_id'])

        return jsonify({
            "message": "Quiz approved successfully",
            "quiz": serialize_quiz(quiz)
        }), 200

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to approve quiz"}), 500


@quiz_bp.route('/<quiz_id>/reject', methods=['PUT'])
@admin_required
def reject_quiz(quiz_id):
    try:
        data = rejection_schema.load(request.get_json())

        quiz = QuizService.reject_quiz(
            quiz_id,
            g.user_id,
            data['reason']
        )

        NotificationService.notify_quiz_rejected(serialize_quiz(quiz), quiz['author_id'])

        return jsonify({
            "message": "Quiz rejected",
            "quiz": serialize_quiz(quiz)
        }), 200

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to reject quiz"}), 500

