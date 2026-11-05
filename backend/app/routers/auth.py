from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.jwt import create_access_token, decode_access_token
from app.core.security import verify_password
from app.models.users import User
from app.schemas.auth import LoginRequest, LoginResponse, LogoutResponse

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"],
)

bearer_scheme = HTTPBearer()


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login Superadmin",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Login menggunakan email dan password superadmin.
    Mengembalikan JWT access token yang dipakai untuk mengakses endpoint terproteksi.
    """
    # 1. Cari user berdasarkan email
    user = db.query(User).filter(User.email == payload.email).first()

    # 2. Validasi — gunakan pesan error yang sama untuk mencegah user enumeration
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun tidak aktif.",
        )

    # 3. Buat dan kembalikan token
    token = create_access_token(user_id=user.id, email=user.email)
    return LoginResponse(
        status="success",
        access_token=token,
        token_type="bearer",
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout",
)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """
    Logout dari sesi aktif.

    Backend memverifikasi bahwa token yang dikirim valid.
    Karena JWT bersifat stateless (tidak disimpan di server),
    logout sepenuhnya ditangani oleh client dengan menghapus token-nya.
    """
    try:
        decode_access_token(credentials.credentials)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau sudah expired.",
        )

    return LogoutResponse(
        status="success",
        message="Logout berhasil.",
    )
