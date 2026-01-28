from flask_mail import Message
from flask import current_app


class EmailService:
    @staticmethod
    def send_role_change_email(user, old_role, new_role):
        """Send role change email - SAFE VERSION"""
        # Check if email sending is suppressed
        if current_app.config.get('MAIL_SUPPRESS_SEND', True):
            current_app.logger.info(f"Email suppressed - Role change for {user.email}")
            return True

        try:
            # Make sure user exists and has email
            if not user or not user.email:
                current_app.logger.error("No user or email for role change email")
                return False

            role_names = {
                'player': 'Igrač',
                'moderator': 'Moderator',
                'admin': 'Administrator'
            }

            subject = "Promena uloge - Quiz Platforma"
            body = f"""
Poštovani/a {user.first_name} {user.last_name},

Vaša uloga na Quiz Platformi je promenjena.

Stara uloga: {role_names.get(old_role, old_role)}
Nova uloga: {role_names.get(new_role, new_role)}

Srdačan pozdrav,
Quiz Platforma Tim
"""

            msg = Message(
                subject=subject,
                recipients=[user.email],
                body=body
            )

            from flask_mail import Mail
            mail = Mail(current_app)
            mail.send(msg)

            current_app.logger.info(f"Role change email sent to {user.email}")
            return True

        except Exception as e:
            current_app.logger.error(f"Greška pri slanju email-a za promjenu uloge: {str(e)}")
            return False

    @staticmethod
    def send_welcome_email(user):
        """Send welcome email - SAFE VERSION"""
        # Check if email sending is suppressed
        if current_app.config.get('MAIL_SUPPRESS_SEND', True):
            current_app.logger.info(f"Email suppressed - Welcome email for {user.email}")
            return True

        try:
            # Make sure user exists and has email
            if not user or not user.email:
                current_app.logger.error("No user or email for welcome email")
                return False

            subject = "Dobrodošli na Quiz Platformu!"
            body = f"""
Poštovani/a {user.first_name} {user.last_name},

Dobrodošli na Quiz Platformu!

Vaš nalog je uspešno kreiran.
Sada možete da igrate kvizove i takmičite se sa drugim igračima.

Vaša uloga: Igrač

Srdačan pozdrav,
Quiz Platforma Tim
"""

            msg = Message(
                subject=subject,
                recipients=[user.email],
                body=body
            )

            from flask_mail import Mail
            mail = Mail(current_app)
            mail.send(msg)

            current_app.logger.info(f"Welcome email sent to {user.email}")
            return True

        except Exception as e:
            current_app.logger.error(f"Greška pri slanju welcome email-a: {str(e)}")
            return False