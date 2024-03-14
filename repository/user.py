from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from auth.models import user


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create_user(self, signup: user) -> bool:
        try:
            self.session.add(signup)
            await self.session.commit()
        except:
            return False
        return True

    async def get_user(self):
        query = select(user)
        result = await self.session.execute(query)
        return result.mappings().all()

    async def get_user_by_email(self, email: str):
        query = select(user).where(user.c.email == email)
        result = await self.session.execute(query)
        return result.mappings().one()
