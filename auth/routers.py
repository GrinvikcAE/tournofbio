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
    prefix='/auth',
    tags=['Auth']
)


@router.post('/login')
async def login(
        email: EmailStr | str = Form(max_length=128),
        password: str = Form(max_length=128, min_length=6),
        session: AsyncSession = Depends(get_async_session)
):
    user_repository = UserRepository(session)
    db_user = await user_repository.get_user_by_field('email', email)
    if db_user is None:
        return "email or password is not valid"
    if await verify_password(password, db_user['hashed_password']):
        token = await create_access_token(db_user)
        response = RedirectResponse(url=f"/{db_user['id']}")
        response.set_cookie(key=COOKIE_NAME, value=token, httponly=True, expires=ACCESS_TOKEN_EXPIRE_MINUTES)
        return response
    else:
        raise HTTPException(status_code=401, detail='Credentials not correct')
        # return await get_root_page(request, session=session)


@router.post('/logout')
async def logout():
    response = RedirectResponse(url='/')
    response.delete_cookie(key=COOKIE_NAME)
    return response


@router.post('/signup')
async def signup(
        # email: EmailStr = Form(max_length=128),
        email: str = Form(max_length=128),
        password: str = Form(max_length=128, min_length=6),
        session: AsyncSession = Depends(get_async_session)
):
    result = {'email': email,
              'hashed_password': await get_password_hash(password)}

    try:
        stmt = insert(user).values(**result)
        await session.execute(stmt)
        await session.commit()
        return "user created successfully"
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail='Credentials not correct')



