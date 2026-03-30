import requests
from flask import current_app
from threading import Thread
import time


class NotificationService:

    @staticmethod
    def get_main_service_url():
        return current_app.config.get('MAIN_SERVICE_URL', 'http://main-service:5000')

    @staticmethod
    def get_internal_headers():
        return {
            'X-Internal-Token': current_app.config.get('INTERNAL_SERVICE_TOKEN', '')
        }

    @staticmethod
    def _post_notification_with_retry(main_service_url, headers, path, payload, max_attempts=3):
        url = f"{main_service_url}{path}"

        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=2
                )

                if response.status_code == 200:
                    return True

                print(
                    f"[Notification] {path} returned {response.status_code} "
                    f"(attempt {attempt}/{max_attempts})"
                )
            except Exception as e:
                print(
                    f"[Notification] Failed {path} (attempt {attempt}/{max_attempts}): {str(e)}"
                )

            if attempt < max_attempts:
                time.sleep(0.25 * attempt)

        return False

    @staticmethod
    def _dispatch_async(path, payload):
        main_service_url = NotificationService.get_main_service_url()
        headers = NotificationService.get_internal_headers()

        Thread(
            target=NotificationService._post_notification_with_retry,
            args=(main_service_url, headers, path, payload),
            daemon=True
        ).start()
        return True

    @staticmethod
    def notify_quiz_created(quiz_data):
        """Notify admins that a new quiz was created"""
        return NotificationService._dispatch_async('/api/notify/quiz-created', quiz_data)

    @staticmethod
    def notify_quiz_approved(quiz_data, author_id):
        """Notify moderator that their quiz was approved"""
        return NotificationService._dispatch_async(
            '/api/notify/quiz-approved',
            {"quiz": quiz_data, "author_id": author_id}
        )

    @staticmethod
    def notify_quiz_rejected(quiz_data, author_id):
        return NotificationService._dispatch_async(
            '/api/notify/quiz-rejected',
            {"quiz": quiz_data, "author_id": author_id}
        )

    @staticmethod
    def notify_quiz_deleted(quiz_data, deleted_by_role):
        return NotificationService._dispatch_async(
            '/api/notify/quiz-deleted',
            {"quiz": quiz_data, "deleted_by_role": deleted_by_role}
        )
