import re
from typing import Tuple

from sqlalchemy import Connection, select
from db.general_tables import User


def test_email(email: str | None, conn: Connection) -> Tuple[bool, str]:
    if email is None:
        return False, "Почта не должна быть пустой"
    if not re.fullmatch(r'[0-9A-Za-z_.]+@[0-9A-Za-z_.]+.[0-9A-Za-z_]+', email):
        return False, "Неверный формат email"
    return True, "Отлично!"


def test_password(password: str | None) -> Tuple[bool, str]:
    if not re.fullmatch(r'[0-9A-Za-z_.-]+', password):
        return False, "Пароль должен состоять из букв латинского алфавита, цифр и '_', '.', '-'"
    elif len(password) < 8:
        return False, "Пароль должен состоять минимум из 8 символов"
    elif not bool(re.search(r'[0-9]', password)):
        return False, "Пароль должен содержать минимум 1 цифру"
    elif not bool(re.search(r'[A-Z]', password)):
        return False, "Пароль должен содержать минимум 1 заглавную букву"
    elif not bool(re.search(r'[a-z]', password)):
        return False, "Пароль должен содержать минимум 1 строчную букву"
    return True, "Отлично!"
