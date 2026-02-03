from app import db
from app.models.user import User, RoleEnum
from app.models.login_attempt import LoginAttempt
from app.utils.password_utils import hash_password, verify_password
from app.utils.jwt_utils import generate_token
from flask import current_app
from datetime import datetime, timedelta

class AuthService:
    FAILED_LOGIN_KEY = "failed_login:{}"
    BLOCKED_KEY = "blocked:{}"
    MAX_FAILED_ATTEMPTS = 3
    BLOCK_DURATION_MINUTES = 1 
    @staticmethod
    def register_user(user_data):
        """Register new user"""
        try:
            # Validate required fields
            errors = {}

            # Check all required fields
            required_fields = ['first_name', 'last_name', 'email', 'password',
                               'date_of_birth', 'gender', 'country', 'street', 'street_number']

            for field in required_fields:
                if not user_data.get(field):
                    errors[field] = f'{field.replace("_", " ").title()} je obavezno polje'

            # Email validation
            email = user_data.get('email', '').strip().lower()
            if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                errors['email'] = 'Nevažeći format email-a'

            # Password validation
            password = user_data.get('password', '')
            if password:
                if len(password) < 8:
                    errors['password'] = 'Lozinka mora imati najmanje 8 karaktera'
                if not re.search(r'[A-Z]', password):
                    errors['password'] = 'Lozinka mora imati barem jedno veliko slovo'
                if not re.search(r'[a-z]', password):
                    errors['password'] = 'Lozinka mora imati barem jedno malo slovo'
                if not re.search(r'\d', password):
                    errors['password'] = 'Lozinka mora imati barem jedan broj'

            if errors:
                return None, errors

            # Check if email already exists
            if User.query.filter_by(email=email).first():
                return None, {'email': 'Email adresa već postoji u sistemu'}

            # Date validation
            try:
                birth_date = datetime.strptime(user_data['date_of_birth'], '%Y-%m-%d').date()
                today = datetime.now().date()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

                if age < 13:
                    return None, {'date_of_birth': 'Morate imati najmanje 13 godina'}
                if birth_date > today:
                    return None, {'date_of_birth': 'Datum rođenja ne može biti u budućnosti'}
            except ValueError:
                return None, {'date_of_birth': 'Nevažeći format datuma. Koristite YYYY-MM-DD'}

            # Create new user
            user = User(
                first_name=user_data['first_name'].strip(),
                last_name=user_data['last_name'].strip(),
                email=email,
                date_of_birth=birth_date,
                gender=user_data['gender'],
                country=user_data['country'].strip(),
                street=user_data['street'].strip(),
                street_number=str(user_data['street_number']).strip(),
                role='player'  # Default role
            )

            # Hash and store password
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            # NOW user has an ID
            print(f"DEBUG: User created with ID: {user.id}")

            # Send welcome email - wrap in try/except so it doesn't break registration
            try:
                EmailService.send_welcome_email(user)
            except Exception as e:
                current_app.logger.error(f"Greška pri slanju welcome email-a: {str(e)}")
                # Don't return error, just log it

            return user, None

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Greška pri registraciji: {str(e)}")
            return None, {'error': f'Greška pri čuvanju podataka: {str(e)}'}

    @staticmethod
    def login_user(email, password):
        """User login with rate limiting"""
        try:
            # Clean input
            email = email.strip().lower() if email else ''

            # Log login attempt (initially as failed)
            attempt = LoginAttempt(
                email=email,
                ip_address=request.remote_addr if request else None,
                user_agent=request.user_agent.string if request and request.user_agent else None,
                success=False
            )
            db.session.add(attempt)

            # Find user
            user = User.query.filter_by(email=email).first()

            if not user:
                db.session.commit()
                return None, {'email': 'Korisnik sa ovim email-om ne postoji'}, None

            # Check if account is active
            if not user.is_active:
                db.session.commit()
                return None, {'account': 'Korisnički nalog je deaktiviran'}, None

            # Check if account is blocked
            if user.is_login_blocked():
                blocked_time = user.get_blocked_time_remaining()
                db.session.commit()
                return None, {
                    'account': f'Prijava je blokirana. Pokušajte ponovo za {blocked_time} sekundi.'
                }, None

            # Verify password
            if not user.check_password(password):
                # Increment failed attempts
                user.failed_login_attempts += 1
                user.last_failed_login = datetime.now(pytz.UTC)

                # Block after 3 failed attempts (1 minute for testing)
                if user.failed_login_attempts >= 3:
                    user.login_blocked_until = datetime.now(pytz.UTC) + timedelta(minutes=1)

                db.session.commit()

                if user.failed_login_attempts >= 3:
                    return None, {
                        'account': 'Previše neuspješnih pokušaja. Pristup blokiran na 1 minut.'
                    }, None
                else:
                    attempts_left = 3 - user.failed_login_attempts
                    return None, {
                        'password': f'Pogrešna lozinka. Preostali pokušaji: {attempts_left}'
                    }, None

            # SUCCESSFUL LOGIN
            # Reset failed attempts
            user.reset_failed_logins()
            # Update login attempt to success
            attempt.success = True
            db.session.commit()

            # Create JWT tokens
            from flask_jwt_extended import create_access_token, create_refresh_token

            additional_claims = {
                'role': user.role,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }

            access_token = create_access_token(
                identity=str(user.id),
                additional_claims=additional_claims
            )

            refresh_token = create_refresh_token(
                identity=str(user.id),
                additional_claims=additional_claims
            )

            return user, None, {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Greška pri prijavi: {str(e)}")
            return None, {'error': str(e)}, None

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        try:
            return User.query.get(int(user_id))
        except:
            return None

    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change password"""
        user = User.query.get(int(user_id))

        if not user:
            return False, 'Korisnik nije pronađen'

        if not user.check_password(current_password):
            return False, 'Trenutna lozinka nije tačna'

        # Validate new password
        if len(new_password) < 8:
            return False, 'Nova lozinka mora imati najmanje 8 karaktera'
        if not re.search(r'[A-Z]', new_password):
            return False, 'Nova lozinka mora imati barem jedno veliko slovo'
        if not re.search(r'[a-z]', new_password):
            return False, 'Nova lozinka mora imati barem jedno malo slovo'
        if not re.search(r'\d', new_password):
            return False, 'Nova lozinka mora imati barem jedan broj'

        user.set_password(new_password)
        db.session.commit()

        return True, 'Lozinka uspješno promijenjena'
