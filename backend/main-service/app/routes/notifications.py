from flask import Blueprint, request, jsonify
from app import socketio
from app.websocket.events import emit_quiz_created, emit_quiz_approved, emit_quiz_rejected, emit_quiz_deleted
from app.services.email_service import EmailService
from app.services.user_service import UserService

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/quiz-created', methods=['POST'])
def notify_quiz_created():
    try:
        quiz_data = request.get_json()
        emit_quiz_created(socketio, quiz_data)
        return jsonify({"message": "Notification sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notifications_bp.route('/quiz-approved', methods=['POST'])
def notify_quiz_approved():
    try:
        data = request.get_json()
        quiz_data = data.get('quiz')
        author_id = data.get('author_id')

        emit_quiz_approved(socketio, quiz_data, author_id)
        return jsonify({"message": "Notification sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notifications_bp.route('/quiz-rejected', methods=['POST'])
def notify_quiz_rejected():
    try:
        data = request.get_json()
        quiz_data = data.get('quiz')
        author_id = data.get('author_id')

        emit_quiz_rejected(socketio, quiz_data, author_id)
        return jsonify({"message": "Notification sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notifications_bp.route('/quiz-deleted', methods=['POST'])
def notify_quiz_deleted():
    try:
        data = request.get_json()
        quiz_data = data.get('quiz')
        deleted_by_role = data.get('deleted_by_role')

        emit_quiz_deleted(socketio, quiz_data, deleted_by_role)
        return jsonify({"message": "Notification sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notifications_bp.route('/send-quiz-result-email', methods=['POST'])
def send_quiz_result_email():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        quiz_title = data.get('quiz_title')
        score = data.get('score')
        max_score = data.get('max_score')
        rank = data.get('rank')

        if not all([user_id, quiz_title is not None, score is not None, max_score is not None, rank is not None]):
            return jsonify({"error": "Missing required fields"}), 400

        user = UserService.get_user(user_id)

        percentage = (score / max_score * 100) if max_score > 0 else 0

        from flask_mail import Message
        from app.services.email_service import mail
        from flask import current_app

        msg = Message(
            subject=f"Quiz Results: {quiz_title}",
            recipients=[user.email],
            body=f"""
Hello {user.first_name} {user.last_name},

Your quiz results are ready!

Quiz: {quiz_title}
Score: {score}/{max_score} ({percentage:.1f}%)
Rank: #{rank}

Best regards,
Quiz Platform Team
            """.strip()
        )

        if current_app.config.get('MAIL_SERVER'):
            mail.send(msg)
        else:
            print(f"[EMAIL] Quiz result email sent to {user.email}")
            print(f"Quiz: {quiz_title}, Score: {score}/{max_score}, Rank: #{rank}")

        return jsonify({"message": "Email sent successfully"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send quiz result email: {str(e)}")
        return jsonify({"error": "Failed to send email"}), 500


@notifications_bp.route('/send-pdf-report', methods=['POST'])
def send_pdf_report():
    try:
        data = request.get_json()
        recipient_email = data.get('recipient_email')
        quiz_title = data.get('quiz_title')
        pdf_data = data.get('pdf_data')  

        if not all([recipient_email, quiz_title, pdf_data]):
            return jsonify({"error": "Missing required fields"}), 400

        import base64
        import io
        pdf_bytes = base64.b64decode(pdf_data)
        pdf_attachment = io.BytesIO(pdf_bytes)

        from flask_mail import Message
        from app.services.email_service import mail
        from flask import current_app

        msg = Message(
            subject=f"Quiz Report: {quiz_title}",
            recipients=[recipient_email],
            body=f"""
Hello,

Please find attached the PDF report for quiz: {quiz_title}

Best regards,
Quiz Platform Team
            """.strip()
        )

        msg.attach(
            f"{quiz_title}_report.pdf",
            "application/pdf",
            pdf_attachment.getvalue()
        )

        if current_app.config.get('MAIL_SERVER'):
            mail.send(msg)
        else:
            print(f"[EMAIL] PDF report sent to {recipient_email}")
            print(f"Quiz: {quiz_title}")

        return jsonify({"message": "PDF report sent successfully"}), 200

    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send PDF report: {str(e)}")
        return jsonify({"error": "Failed to send PDF report"}), 500
