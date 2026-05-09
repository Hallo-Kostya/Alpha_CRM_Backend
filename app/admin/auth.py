from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from app.services.auth_service import AuthService
from app.infrastructure.database.repositories.curator_repository import CuratorRepository
from app.infrastructure.database.database import db_helper


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")
        
        async with db_helper.async_session_factory() as session:
            repo = CuratorRepository(session)
            total, curators = await repo.get_list(filters={"email": email})
            if not curators:
                return False
            
            curator = curators[0]
            auth = AuthService(None)
            if not auth.verify_password(password, curator.hashed_password):
                return False
            
            request.session.update({"admin_user": email})
            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return "admin_user" in request.session