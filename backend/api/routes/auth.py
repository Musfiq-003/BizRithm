# backend/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import uuid

from backend.core.database import get_db
from backend.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from backend.core.logger import logger
from backend.models.user import User
from backend.schemas.user import UserRegister, UserLogin, TokenResponse, TokenRefresh, UserResponse
from backend.api.middleware.auth_middleware import get_current_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    # Check existing email
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check existing username
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=data.email,
        username=data.username,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        company_name=data.company_name,
        role="analyst",
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
    logger.info(f"New user registered: {user.email}")

    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return tokens."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    # Update last login
    user.last_login = datetime.now(timezone.utc)

    token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
    logger.info(f"User logged in: {user.email}")

    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(data: TokenRefresh):
    """Refresh access token using refresh token."""
    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="Invalid refresh token")

    new_access = create_access_token({
        "sub": payload["sub"],
        "email": payload.get("email"),
        "role": payload.get("role"),
    })
    return {"access_token": new_access, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout (client-side token invalidation)."""
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}
