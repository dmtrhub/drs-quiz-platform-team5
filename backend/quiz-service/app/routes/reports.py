from flask import Blueprint, send_file, jsonify, g, current_app
from app.services.report_service import ReportService
from app.utils.auth_helper import token_required, admin_required
import requests

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/quiz/<quiz_id>', methods=['POST'])
@admin_required
def generate_quiz_report(quiz_id):
    try:
        pdf_buffer, filename = ReportService.generate_quiz_report(quiz_id)

        main_service_url = current_app.config.get('MAIN_SERVICE_URL', 'http://localhost:5000')
        response = requests.get(f"{main_service_url}/users/{g.user_id}/public")

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch user information"}), 500

        user_data = response.json().get('user', {})
        admin_email = user_data.get('email')

        if not admin_email:
            return jsonify({"error": "Admin email not found"}), 500

        admin_email = 'REPLACE@gmail.com'

        import base64
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')

        email_data = {
            'recipient_email': admin_email,
            'quiz_title': filename,
            'pdf_data': pdf_base64
        }

        email_response = requests.post(
            f"{main_service_url}/api/notify/send-pdf-report",
            json=email_data
        )

        if email_response.status_code == 200:
            return jsonify({"message": "PDF report has been sent to your email"}), 200
        else:
            return jsonify({"error": "Failed to send PDF report"}), 500

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(f"[REPORT ERROR] {str(e)}")
        return jsonify({"error": "Failed to generate report"}), 500


@reports_bp.route('/result/<result_id>', methods=['GET'])
@token_required
def generate_user_report(result_id):
    try:
        user_info = {
            'user_id': g.user_id,
            'email': g.user_email,
            'first_name': 'User',  
            'last_name': str(g.user_id)
        }

        pdf_buffer, filename = ReportService.generate_user_report(result_id, user_info)

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{filename}.pdf"
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Failed to generate report"}), 500
