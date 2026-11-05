import os

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.users import User


def seed_superadmin(db: Session) -> None:
    """
    Membuat akun superadmin jika belum ada di database.
    Dipanggil otomatis saat server startup.
    """
    email = os.getenv("SUPERADMIN_EMAIL", "admin@plts.com")
    password = os.getenv("SUPERADMIN_PASSWORD", "")

    if not password:
        print("[Seeder] SUPERADMIN_PASSWORD belum dikonfigurasi di .env, skip seeding.")
        return

    # Cek apakah akun sudah ada (idempotent — aman dijalankan berulang kali)
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(f"[Seeder] Superadmin '{email}' sudah ada di database, skip seeding.")
        return

    superadmin = User(
        email=email,
        password=hash_password(password),
        is_active=True,
    )
    db.add(superadmin)
    db.commit()
    print(f"[Seeder] Superadmin '{email}' berhasil dibuat.")
