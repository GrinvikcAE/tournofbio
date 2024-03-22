from pydantic import EmailStr
from repository.user import UserRepository
from security.secr import verify_password, create_access_token, get_password_hash
from security.secr import get_admin_status_from_cookie, get_current_user_from_cookie
from auth.models import user
from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from security.secr import COOKIE_NAME, ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy import insert, update, select

router = APIRouter(
    prefix='/adm',
    tags=['Adm']
)


@router.get("")
async def admin_panel(user_status: bool = Depends(get_admin_status_from_cookie)):
    if not user_status:
        raise HTTPException(status_code=401, detail='Unauthorized as superuser')
    else:
        return RedirectResponse(url='/admin')


@router.post('/update_value_to_user', dependencies=[Depends(get_admin_status_from_cookie)])
async def update_value(email: EmailStr = Form(max_length=128),
                       field: str = Form(max_length=128),
                       value: int | str | bool = Form(max_length=128),
                       user_status: bool = Depends(get_admin_status_from_cookie),
                       session: AsyncSession = Depends(get_async_session)):
    if user_status:
        if 'id' in field:
            value = int(value)
            result = {f'{field}': value}
        elif field == 'is_superuser':
            value = True if value.lower() == 'true' else False
            role_id = 1 if value else 6
            result = {f'{field}': value,
                      'role_id': role_id}
        else:
            result = {f'{field}': value}
        stmt = update(user).where(user.c.email == email).values(**result)
        await session.execute(stmt)
        await session.commit()
        return 'User updated successfully'
    else:
        raise HTTPException(status_code=401, detail='Unauthorized as superuser')