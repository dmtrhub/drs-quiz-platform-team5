from flask import current_app
from flask_mail import Mail, Message

mail = Mail()


class EmailService:
    @staticmethod
    def init_mail(app):
        mail.init_app(app)

    @staticmethod
    def send_registration_email(user):
        try:
            msg = Message(
                subject="Welcome to Quiz Platform!",
                recipients=[user.email],
                body=f"""
Hello {user.first_name} {user.last_name},

Welcome to Quiz Platform! Your account has been successfully created.

Email: {user.email}
Role: {user.role.value}

You can now log in and start taking quizzes!

Best regards,
Quiz Platform Team
                """.strip()
            )

            if current_app.config.get('MAIL_SERVER'):
                mail.send(msg)
                return True
            else:
                print(f"[EMAIL] Registration email sent to {user.email}")
                return True

        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send registration email: {str(e)}")
            return False

    @staticmethod
    def send_role_change_email(user, old_role, new_role):
        try:
            msg = Message(
                subject="Your Role Has Been Updated",
                recipients=[user.email],
                body=f"""
Hello {user.first_name} {user.last_name},

Your role on Quiz Platform has been updated.

Previous Role: {old_role}
New Role: {new_role}

This change will affect your permissions on the platform. Please sign out and then sign in again on platform.

Best regards,
Quiz Platform Team
                """.strip()
            )

            if current_app.config.get('MAIL_SERVER'):
                mail.send(msg)
                return True
            else:
                print(f"[EMAIL] Role change email sent to {user.email}")
                return True

        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send role change email: {str(e)}")
            return False
