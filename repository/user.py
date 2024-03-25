from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
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

    async def get_user_by_field(self, field: str, value: str | int):
        match field:
            case 'id':
                query = select(user).where(user.c.id == int(value))
            case 'email':
                query = select(user).where(user.c.email == value)
            case _:
                return False
        result = await self.session.execute(query)
        return result.mappings().one_or_none()

    async def update_user_role(self, email: str, role_id: int):
        try:
            query = update(user).where(user.c.email == email).values(role_id=role_id)
            await self.session.execute(query)
            await self.session.commit()
        except:
            return False
        return True
