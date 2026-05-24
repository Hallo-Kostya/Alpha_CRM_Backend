from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_current_curator
from app.schemas.curator import CuratorPOST, Curator, CuratorLogin
from app.schemas.auth import TokenPairResponse
from app.services.curator_service import CuratorService, curator_service_getter
from app.services.auth_service import AuthService, auth_service_getter
from app.infrastructure.database.models import CuratorModel

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=TokenPairResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    data: CuratorPOST,
    service: CuratorService = Depends(curator_service_getter),
):
    """Register new curator and return token pair."""
    result = await service.register_curator(data)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    access, refresh = result
    return TokenPairResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenPairResponse)
async def login(
    data: CuratorLogin,
    service: CuratorService = Depends(curator_service_getter),
):
    """Login curator and return token pair."""
    result = await service.login_curator(data)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    access, refresh = result
    return TokenPairResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh(
    refresh_token: str,
    auth_service: AuthService = Depends(auth_service_getter),
):
    """Refresh token pair using refresh token."""
    try:
        curator_id = auth_service.get_curator_id_from_refresh(refresh_token)
        pair = await auth_service.refresh_token_pair(refresh_token, curator_id)
        access, refresh = pair
        return TokenPairResponse(access_token=access, refresh_token=refresh)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked refresh token",
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_token: str,
    auth_service: AuthService = Depends(auth_service_getter),
    current_curator: CuratorModel = Depends(get_current_curator),
):
    """Logout curator by revoking refresh token."""
    try:
        await auth_service.revoke_token_pair(refresh_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already revoked or invalid",
        )
    return None


@router.get("/me", response_model=Curator)
async def me(
    current_curator: CuratorModel = Depends(get_current_curator),
):
    """Get current curator profile."""
    from app.schemas.curator import Curator

    return Curator.model_validate(current_curator, from_attributes=True)
