import requests
from flask import current_app


class NotificationService:

    @staticmethod
    def get_main_service_url():
        return current_app.config.get('MAIN_SERVICE_URL', 'http://main-service:5000')

    @staticmethod
    def notify_quiz_created(quiz_data):
        """Notify admins that a new quiz was created"""
        try:
            response = requests.post(
                f"{NotificationService.get_main_service_url()}/api/notify/quiz-created",
                json=quiz_data,
                timeout=5
            )
            print(f"[Notification] Quiz created notification sent: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"[Notification] Failed to send quiz created notification: {str(e)}")
            return False

    @staticmethod
    def notify_quiz_approved(quiz_data, author_id):
        """Notify moderator that their quiz was approved"""
        try:
            response = requests.post(
                f"{NotificationService.get_main_service_url()}/api/notify/quiz-approved",
                json={"quiz": quiz_data, "author_id": author_id},
                timeout=5
            )
            print(f"[Notification] Quiz approved notification sent: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"[Notification] Failed to send quiz approved notification: {str(e)}")
            return False

    @staticmethod
    def notify_quiz_rejected(quiz_data, author_id):
        try:
            response = requests.post(
                f"{NotificationService.get_main_service_url()}/api/notify/quiz-rejected",
                json={"quiz": quiz_data, "author_id": author_id},
                timeout=5
            )
            print(f"[Notification] Quiz rejected notification sent: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"[Notification] Failed to send quiz rejected notification: {str(e)}")
            return False

    @staticmethod
    def notify_quiz_deleted(quiz_data, deleted_by_role):
        try:
            response = requests.post(
                f"{NotificationService.get_main_service_url()}/api/notify/quiz-deleted",
                json={"quiz": quiz_data, "deleted_by_role": deleted_by_role},
                timeout=5
            )
            print(f"[Notification] Quiz deleted notification sent: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"[Notification] Failed to send quiz deleted notification: {str(e)}")
            return False
