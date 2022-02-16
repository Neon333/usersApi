import bcrypt


def hash_password(source: str) -> str:
    return bcrypt.hashpw(source.encode(), bcrypt.gensalt()).decode()


def verify(password: str, stored_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), stored_password.encode())
