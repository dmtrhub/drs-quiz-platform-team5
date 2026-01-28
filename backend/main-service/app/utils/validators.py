import re


def validate_phone_number(phone):
    """Validate phone number"""
    if not phone:
        return False

    # Remove all non-numeric characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)

    # Minimum 7, maximum 15 digits (with +)
    if not 7 <= len(cleaned) <= 15:
        return False

    # Must start with + or number
    if cleaned.startswith('+'):
        return cleaned[1:].isdigit()
    else:
        return cleaned.isdigit()


def validate_postal_code(postal_code, country='RS'):
    """Validate postal code by country"""
    if not postal_code:
        return False

    postal_code = str(postal_code).strip()

    if country == 'RS':
        # Serbia - 5 digits
        return bool(re.match(r'^\d{5}$', postal_code))
    elif country == 'BA':
        # Bosnia and Herzegovina - 5 digits
        return bool(re.match(r'^\d{5}$', postal_code))
    elif country == 'ME':
        # Montenegro - 5 digits
        return bool(re.match(r'^\d{5}$', postal_code))
    elif country == 'HR':
        # Croatia - 5 digits
        return bool(re.match(r'^\d{5}$', postal_code))
    else:
        # Default - check if all digits
        return postal_code.isdigit() and 3 <= len(postal_code) <= 10


def sanitize_input(text, max_length=None, allow_html=False):
    """Sanitize user input"""
    if text is None:
        return ''

    text = str(text)

    # Remove leading/trailing whitespace
    text = text.strip()

    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)

    if not allow_html:
        # Remove potentially harmful HTML/JS tags
        text = re.sub(r'<[^>]*>', '', text)
        # Remove potentially dangerous JavaScript calls
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'on\w+=', '', text, flags=re.IGNORECASE)

    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]

    return text


def validate_name(name):
    """Validate first and last name"""
    if not name:
        return False, "Polje je obavezno"

    name = name.strip()

    if len(name) < 2:
        return False, "Mora imati najmanje 2 karaktera"

    if len(name) > 50:
        return False, "Može imati najviše 50 karaktera"

    # Allow letters, dashes and apostrophes
    if not re.match(r'^[A-Za-zČĆŽŠĐčćžšđ\-\'\s]+$', name):
        return False, "Može sadržati samo slova, crtice i apostrofe"

    return True, ""