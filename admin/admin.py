from fastapi import Request
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import AsyncSession
from repository.user import UserRepository
from security.secr import verify_password, create_access_token


class AdminAuth(AuthenticationBackend):

    def __init__(self, session: AsyncSession, secret_key: str):
        super().__init__(secret_key)
        self.session: AsyncSession = session

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form['username'], form['password']
        user_repository = UserRepository(session=self.session)
        user_db = await user_repository.get_user_by_email(email=email)
        if user_db is not None and user_db['is_superuser'] is True:
            if await verify_password(password, user_db['hashed_password']):
                token = await create_access_token(user_db)
                request.session.update({'token': token})
                return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        return True



