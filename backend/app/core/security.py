import bcrypt


def hash_password(plain_password: str) -> str:
    """Hash password menggunakan bcrypt."""
    return bcrypt.hashpw(
        plain_password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikasi password dengan hash yang tersimpan di database."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )
