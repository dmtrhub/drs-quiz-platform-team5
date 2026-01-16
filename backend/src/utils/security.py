import re
from datetime import datetime, date
from flask_jwt_extended import create_access_token, create_refresh_token
from dateutil.relativedelta import relativedelta


def validate_email(email):
    """Validate email address"""
    if not email:
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip().lower()) is not None


def validate_password(password):
    """Validate password"""
    if not password:
        return False, "Lozinka je obavezna"

    if len(password) < 8:
        return False, "Lozinka mora imati najmanje 8 karaktera"

    if not re.search(r'[A-Z]', password):
        return False, "Lozinka mora imati barem jedno veliko slovo"

    if not re.search(r'[a-z]', password):
        return False, "Lozinka mora imati barem jedno malo slovo"

    if not re.search(r'\d', password):
        return False, "Lozinka mora imati barem jedan broj"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Lozinka mora imati barem jedan specijalni karakter"

    return True, ""


def create_tokens(identity, additional_claims=None):
    """Create access and refresh tokens"""
    if additional_claims is None:
        additional_claims = {}

    access_token = create_access_token(
        identity=identity,
        additional_claims=additional_claims
    )

    refresh_token = create_refresh_token(
        identity=identity,
        additional_claims=additional_claims
    )

    return access_token, refresh_token


def validate_user_data(data, for_update=False):
    """Validate user data"""
    errors = {}

    # First name
    if 'first_name' in data:
        first_name = data['first_name'].strip() if data['first_name'] else ''
        if not first_name:
            errors['first_name'] = 'Ime je obavezno'
        elif len(first_name) < 2:
            errors['first_name'] = 'Ime mora imati najmanje 2 karaktera'
        elif len(first_name) > 50:
            errors['first_name'] = 'Ime može imati najviše 50 karaktera'

    # Last name
    if 'last_name' in data:
        last_name = data['last_name'].strip() if data['last_name'] else ''
        if not last_name:
            errors['last_name'] = 'Prezime je obavezno'
        elif len(last_name) < 2:
            errors['last_name'] = 'Prezime mora imati najmanje 2 karaktera'
        elif len(last_name) > 50:
            errors['last_name'] = 'Prezime može imati najviše 50 karaktera'

    # Email (only for registration, not for update unless explicitly provided)
    if not for_update and 'email' in data:
        email = data['email'].strip().lower() if data['email'] else ''
        if not email:
            errors['email'] = 'Email je obavezan'
        elif not validate_email(email):
            errors['email'] = 'Nevažeći email format'

    # Date of birth
    if 'date_of_birth' in data:
        dob_str = data['date_of_birth']
        if not dob_str:
            errors['date_of_birth'] = 'Datum rođenja je obavezan'
        else:
            try:
                birth_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
                today = date.today()

                # Check if date is in future
                if birth_date > today:
                    errors['date_of_birth'] = 'Datum rođenja ne može biti u budućnosti'

                # Check if user is at least 13 years old
                min_age_date = today - relativedelta(years=13)
                if birth_date > min_age_date:
                    errors['date_of_birth'] = 'Morate imati najmanje 13 godina'

                # Check if date is realistic (not too far in past)
                max_age_date = today - relativedelta(years=120)
                if birth_date < max_age_date:
                    errors['date_of_birth'] = 'Datum rođenja nije validan'

            except ValueError:
                errors['date_of_birth'] = 'Format datuma nije validan (YYYY-MM-DD)'

    # Gender
    if 'gender' in data:
        valid_genders = ['male', 'female', 'other']
        gender = data['gender']
        if gender not in valid_genders:
            errors['gender'] = f'Pol mora biti jedan od: {", ".join(valid_genders)}'

    # Address fields
    address_fields = {
        'country': 'Država',
        'street': 'Ulica',
        'street_number': 'Broj'
    }

    for field, display_name in address_fields.items():
        if field in data:
            value = str(data[field]).strip() if data[field] is not None else ''
            if not value:
                errors[field] = f'{display_name} je obavezan'
            elif len(value) > 100 and field == 'country':
                errors[field] = f'{display_name} može imati najviše 100 karaktera'
            elif len(value) > 200 and field == 'street':
                errors[field] = f'{display_name} može imati najviše 200 karaktera'
            elif len(value) > 20 and field == 'street_number':
                errors[field] = f'{display_name} može imati najviše 20 karaktera'

    return errors


def get_current_timestamp():
    """Get current timestamp"""
    return datetime.now().isoformat()