# app/presentation/api/v1/routers/auth/routes.py

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from app.application.dtos.auth_dto import (
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    ProfilePhotoResponse,
    UserProfileResponse,
    LoginResponse,
    LogoutResponse,
    TokenResponse,
    MessageResponse,
    ForgotPasswordResponse,
)
from app.application.dtos.user_dto import CreateUserRequest, CreateUserResponse, UpdateUserRequest
from app.application.services.user_application_service import UserApplicationService
from app.domain.services.user_service import UserService
from app.common.exceptions import AppException
from app.infrastructure.security.password_hasher import PasswordHasher
from app.infrastructure.security.jwt_handler import JWTHandler
from app.infrastructure.persistence.user_repository import UserRepository
from app.infrastructure.persistence.member_repository import MemberRepository
from app.infrastructure.persistence.identity_repository import DigitalIdentityRepository
from app.core.config import settings, PROJECT_ROOT
from app.presentation.api.v1.dependencies import get_current_user_id


# Router for authentication endpoints
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"]
)


# Dependency to get auth service
async def get_auth_service():
    """Get authentication service"""
    # Create service instances
    password_hasher = PasswordHasher()
    jwt_handler = JWTHandler(
        secret_key=settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        access_token_expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    user_repository = UserRepository()
    
    # Return service
    from app.application.services.auth_service import AuthServiceImpl
    return AuthServiceImpl(password_hasher, jwt_handler, user_repository)


async def get_user_application_service() -> UserApplicationService:
    """Get user application service"""
    repository = UserRepository()
    domain_service = UserService(repository)
    return UserApplicationService(domain_service)


async def _resolve_qr_token_for_user(auth_service, user_id: str) -> str | None:
    """Resolve a QR token for a user from member history or digital identity."""
    try:
        member = await auth_service.member_repository.find_by_user_id(str(user_id))
        if member:
            for entry in reversed(getattr(member, "audit_log", []) or []):
                metadata = getattr(entry, "metadata", None) or {}
                qr_token = metadata.get("qr_token")
                if qr_token:
                    return qr_token
    except Exception:
        pass

    try:
        identity_repo = DigitalIdentityRepository()
        identity = await identity_repo.get_by_user_id(str(user_id))
        if identity:
            qr_token = getattr(identity, "qr_token", None)
            if qr_token:
                return qr_token
    except Exception:
        pass

    return None


@router.post(
    "/register",
    response_model=CreateUserResponse,
    status_code=201,
    summary="Register new user",
    description="Create a new user account"
)
async def register(
    request: RegisterRequest,
    user_service: UserApplicationService = Depends(get_user_application_service)
) -> CreateUserResponse:
    """User registration endpoint"""
    try:
        create_request = CreateUserRequest(
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            password=request.password,
            organization_id=""
        )
        return await user_service.create_user(create_request)
    except HTTPException:
        raise
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=200,
    summary="User login",
    description="Login with email and password to get access and refresh tokens"
)
async def login(
    request: LoginRequest,
    auth_service = Depends(get_auth_service)
) -> LoginResponse:
    """User login endpoint"""
    try:
        result = await auth_service.authenticate(
            email=request.email,
            password=request.password
        )
        
        if not result:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user, access_token, refresh_token, membership_status, membership_number = result

        qr_token = await _resolve_qr_token_for_user(auth_service, str(user.id))
        
        membership_review_comments = None
        membership_rejected_at = None
        try:
            member = await auth_service.member_repository.find_by_user_id(str(user.id))
            if member:
                membership_review_comments = member.review_comments
                membership_rejected_at = member.rejected_at
        except Exception:
            pass

        user_profile = UserProfileResponse(
            id=str(user.id),
            email=str(user.email),
            first_name=user.first_name,
            last_name=user.last_name,
            phone=str(user.phone) if user.phone is not None else None,
            profile_photo_url=user.profile_photo_url,
            roles=[str(role) for role in user.roles],
            mfa_enabled=user.mfa_enabled,
            status=user.status.value if hasattr(user.status, 'value') else str(user.status),
            membership_status=membership_status,
            membership_number=membership_number,
            membership_review_comments=membership_review_comments,
            membership_rejected_at=membership_rejected_at,
            qr_token=qr_token,
            last_login_at=user.last_login_at,
            created_at=user.created_at
        )
        
        token = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return LoginResponse(user=user_profile, token=token)
    
    except HTTPException:
        raise
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    status_code=200,
    summary="Request password reset",
    description="Request a password reset token for the provided email"
)
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service = Depends(get_auth_service)
) -> ForgotPasswordResponse:
    """Forgot password endpoint"""
    try:
        reset_token = await auth_service.generate_password_reset_token(request.email)
        if not reset_token:
            return ForgotPasswordResponse(
                message="If the email exists, password reset instructions have been sent."
            )
        return ForgotPasswordResponse(
            message="Password reset instructions generated.",
            reset_token=reset_token
        )
    except HTTPException:
        raise
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=200,
    summary="Reset password",
    description="Reset password using a password reset token"
)
async def reset_password(
    request: ResetPasswordRequest,
    auth_service = Depends(get_auth_service)
) -> MessageResponse:
    """Reset password endpoint"""
    try:
        success = await auth_service.reset_password(request.token, request.new_password)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        return MessageResponse(message="Password has been reset successfully.")
    except HTTPException:
        raise
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=200,
    summary="Change password",
    description="Change password for the currently authenticated user"
)
async def change_password(
    request: ChangePasswordRequest,
    auth_service = Depends(get_auth_service),
    user_id: str = Depends(get_current_user_id)
) -> MessageResponse:
    """Change current user password"""
    try:
        success = await auth_service.change_password(
            user_id=user_id,
            current_password=request.current_password,
            new_password=request.new_password
        )
        if not success:
            raise HTTPException(status_code=400, detail="Invalid current password")
        return MessageResponse(message="Password changed successfully.")
    except HTTPException:
        raise
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=200,
    summary="Refresh access token",
    description="Refresh access token using a valid refresh token"
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service = Depends(get_auth_service)
) -> TokenResponse:
    """Refresh access token endpoint"""
    try:
        new_access_token = await auth_service.refresh_access_token(
            refresh_token=request.refresh_token
        )

        if not new_access_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=request.refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except HTTPException:
        raise
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=200,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user"
)
async def get_current_user(
    auth_service = Depends(get_auth_service),
    request: Request = None
) -> UserProfileResponse:
    """Get current user profile"""
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        user = await auth_service.get_current_user(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token or user not found")

        payload = auth_service.jwt_handler.verify_access_token(token) or {}
        membership_status = payload.get("membership_status")
        membership_number = payload.get("membership_number")

        qr_token = await _resolve_qr_token_for_user(auth_service, str(user.id))
        membership_review_comments = None
        membership_rejected_at = None
        try:
            member = await auth_service.member_repository.find_by_user_id(str(user.id))
            if member:
                membership_status = member.status.value
                membership_number = member.membership_number
                membership_review_comments = member.review_comments
                membership_rejected_at = member.rejected_at
        except Exception:
            pass
        
        return UserProfileResponse(
            id=str(user.id),
            email=str(user.email),
            first_name=user.first_name,
            last_name=user.last_name,
            phone=str(user.phone) if user.phone is not None else None,
            profile_photo_url=user.profile_photo_url,
            roles=[str(role) for role in user.roles],
            mfa_enabled=user.mfa_enabled,
            status=user.status.value if hasattr(user.status, 'value') else str(user.status),
            membership_status=membership_status,
            membership_number=membership_number,
            membership_review_comments=membership_review_comments,
            membership_rejected_at=membership_rejected_at,
            qr_token=qr_token,
            last_login_at=user.last_login_at,
            created_at=user.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.put(
    "/me",
    response_model=UserProfileResponse,
    status_code=200,
    summary="Update current user profile",
    description="Update the profile of the currently authenticated user"
)
async def update_current_user(
    request: UpdateUserRequest,
    user_service: UserApplicationService = Depends(get_user_application_service),
    auth_service = Depends(get_auth_service),
    user_id: str = Depends(get_current_user_id)
) -> UserProfileResponse:
    """Update current user profile"""
    try:
        user = await user_service.update_user(user_id, request)

        membership_status = None
        membership_number = None
        membership_review_comments = None
        membership_rejected_at = None
        try:
            member = await auth_service.member_repository.find_by_user_id(str(user.id))
            if member:
                membership_status = member.status.value
                membership_number = member.membership_number
                membership_review_comments = member.review_comments
                membership_rejected_at = member.rejected_at
        except Exception:
            pass

        qr_token = await _resolve_qr_token_for_user(auth_service, str(user.id))

        return UserProfileResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            profile_photo_url=user.profile_photo_url,
            roles=user.roles,
            mfa_enabled=user.mfa_enabled,
            status=user.status,
            membership_status=membership_status,
            membership_number=membership_number,
            membership_review_comments=membership_review_comments,
            membership_rejected_at=membership_rejected_at,
            qr_token=qr_token,
            last_login_at=user.last_login_at,
            created_at=user.created_at
        )
    except HTTPException:
        raise
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/me/photo",
    response_model=ProfilePhotoResponse,
    status_code=200,
    summary="Upload profile photo",
    description="Upload a profile photo for the currently authenticated user"
)
async def upload_profile_photo(
    photo: UploadFile = File(...),
    user_service: UserApplicationService = Depends(get_user_application_service),
    user_id: str = Depends(get_current_user_id),
    request: Request = None,
) -> ProfilePhotoResponse:
    """Upload profile photo endpoint"""
    try:
        upload_dir = PROJECT_ROOT / settings.UPLOAD_DIR
        upload_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(photo.filename).suffix
        filename = f"{uuid4().hex}{suffix}"
        file_path = upload_dir / filename

        contents = await photo.read()
        file_path.write_bytes(contents)

        profile_url = f"/uploads/{filename}"
        update_request = UpdateUserRequest(profile_photo_url=profile_url)
        await user_service.update_user(user_id, update_request)

        member_repository = MemberRepository()
        member = await member_repository.find_by_user_id(user_id)
        if member:
            member.profile_photo_url = profile_url
            member.updated_at = datetime.utcnow()
            await member_repository.save(member)

        return ProfilePhotoResponse(url=profile_url)
    except HTTPException:
        raise
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=200,
    summary="User logout",
    description="Logout the current user and invalidate their tokens"
)
async def logout(request: Request) -> LogoutResponse:
    """User logout endpoint"""
    try:
        # In production, you would:
        # 1. Add the token to a blacklist
        # 2. Invalidate any refresh tokens
        # 3. Clear any session data
        return LogoutResponse(message="Successfully logged out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
