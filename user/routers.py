from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import insert, select, delete, update
from command.models import command, member
from auth.models import role, user
from security.secr import get_current_user_from_cookie

from security.secr import COOKIE_NAME, ACCESS_TOKEN_EXPIRE_MINUTES
from repository.user import UserRepository
from security.secr import create_access_token

router = APIRouter(
    prefix='/user',
    tags=['User']
)


@router.post('/add_command', dependencies=[Depends(get_current_user_from_cookie)])
async def add_command(name: str = Form(max_length=128),
                      current_user=Depends(get_current_user_from_cookie),
                      session: AsyncSession = Depends(get_async_session)):
    try:
        if current_user is None:
            raise HTTPException(status_code=401, detail='Unauthorized')
        elif current_user['role_id'] == 5:
            raise HTTPException(status_code=401, detail='Credentials not correct')
        elif current_user['role_id'] == 6 or len(current_user['commands_name'][0]['commands']) < 1:
            result = [{'commands': [name,]}]
            try:
                stmt = insert(command).values(name=name)
                await session.execute(stmt)
                await session.commit()

                stmt = update(user).where(user.c.email == current_user['email']).values(commands_name=result)
                await session.execute(stmt)
                await session.commit()
                return 'Command added successfully'
            except:
                raise HTTPException(status_code=422, detail='Credentials not correct')
        else:
            stmt = select(user).where(user.c.email == current_user['email'])
            result = await session.execute(stmt)
            result = result.mappings().all()
            temp = result[0]['commands_name'][0]['commands'] + [name, ]
            result[0]['commands_name'][0]['commands'] = temp
            stmt = update(user).where(user.c.email == current_user['email']).values(commands_name=result[0]['commands_name'])
            await session.execute(stmt)
            await session.commit()

            user_repository = UserRepository(session)
            db_user = await user_repository.get_user_by_field('email', current_user['email'])
            token = await create_access_token(db_user)
            response = RedirectResponse(url=f"/{current_user['id']}", status_code=302)
            response.set_cookie(key=COOKIE_NAME, value=token, httponly=True, expires=ACCESS_TOKEN_EXPIRE_MINUTES)
            return response
    except:
        raise HTTPException(status_code=404, detail='Credentials not correct')


@router.post('/update_value', dependencies=[Depends(get_current_user_from_cookie)])
async def update_value(field: str = Form(max_length=128),
                       value: int | str = Form(max_length=128),
                       current_user=Depends(get_current_user_from_cookie),
                       session: AsyncSession = Depends(get_async_session)):
    try:
        if current_user is None:
            raise HTTPException(status_code=401, detail='Unauthorized')
        else:
            if field == 'role_id' and int(value) in (3, 4, 5):
                result = {f'{field}': int(value)}
                stmt = update(user).where(user.c.email == current_user['email']).values(**result)
                await session.execute(stmt)
                await session.commit()
                return 'Role updated successfully'
            elif field not in ('role_id', 'hashed_password', 'is_superuser'):
                result = {f'{field}': value}
                stmt = update(user).where(user.c.email == current_user['email']).values(**result)
                await session.execute(stmt)
                await session.commit()
                return f'{field} updated successfully'
            else:
                raise HTTPException(status_code=422, detail='Credentials not correct')
    except:
        raise HTTPException(status_code=422, detail='Credentials not correct')
