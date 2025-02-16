import re


def validate_name(name):
    pattern = (r'^[А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)? [А-ЯЁ][а-яё]+(?:-[А-ЯЁ]['
               r'а-яё]+)?(?: [А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)?)?$')
    return bool(re.fullmatch(pattern, name)) and len(name) <= 254
