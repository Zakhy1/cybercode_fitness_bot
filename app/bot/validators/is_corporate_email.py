import re


def is_corporate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@(cybercode\.pro|pgpi\.su)$'
    return bool(re.fullmatch(pattern, email))
