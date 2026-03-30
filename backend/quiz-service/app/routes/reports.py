from flask import Blueprint, send_file, jsonify, g, current_app, request
from app.services.report_service import ReportService
from app.utils.auth_helper import token_required, admin_required
from threading import Thread
import time
import requests

reports_bp = Blueprint('reports', __name__)


def _send_quiz_report_email_async(main_service_url, email_data, internal_token):
    for attempt in range(1, 4):
        try:
            response = requests.post(
                f"{main_service_url}/api/notify/send-pdf-report",
                json=email_data,
                headers={'X-Internal-Token': internal_token},
                timeout=20
            )

            if response.status_code == 200:
                return

            print(
                f"[REPORT WARNING] Async email notification returned {response.status_code} "
                f"(attempt {attempt}/3)"
            )
        except requests.exceptions.RequestException as e:
            print(f"[REPORT WARNING] Async email notification failed (attempt {attempt}/3): {str(e)}")

        if attempt < 3:
            time.sleep(0.4 * attempt)


@reports_bp.route('/quiz/<quiz_id>', methods=['POST'])
@admin_required
def generate_quiz_report(quiz_id):
    try:
        pdf_buffer, filename = ReportService.generate_quiz_report(quiz_id)

        main_service_url = current_app.config.get('MAIN_SERVICE_URL', 'http://localhost:5000')
        admin_email = g.user_email
        internal_token = current_app.config.get('INTERNAL_SERVICE_TOKEN', '')

        if not admin_email:
            return jsonify({"error": "Admin email not found"}), 500

        import base64
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')

        email_data = {
            'recipient_email': admin_email,
            'quiz_title': filename,
            'pdf_data': pdf_base64
        }

        Thread(
            target=_send_quiz_report_email_async,
            args=(main_service_url, email_data, internal_token),
            daemon=True
        ).start()

        return jsonify({
            "message": "PDF report generated and queued for email delivery"
        }), 202

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
            'first_name': getattr(g, 'user_first_name', '') or 'User',
            'last_name': getattr(g, 'user_last_name', '') or str(g.user_id)
        }

        main_service_url = current_app.config.get('MAIN_SERVICE_URL', 'http://localhost:5000')
        auth_header = request.headers.get('Authorization', '')

        if auth_header:
            try:
                response = requests.get(
                    f"{main_service_url}/users/{g.user_id}",
                    headers={'Authorization': auth_header},
                    timeout=5
                )
                if response.status_code == 200:
                    user_data = response.json().get('user', {})
                    user_info['first_name'] = user_data.get('first_name') or user_info['first_name']
                    user_info['last_name'] = user_data.get('last_name') or user_info['last_name']
                    user_info['email'] = user_data.get('email') or user_info['email']
            except Exception:
                pass

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
