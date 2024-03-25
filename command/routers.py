from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from security.secr import COOKIE_NAME, ACCESS_TOKEN_EXPIRE_MINUTES
from security.secr import get_admin_status_from_cookie, get_current_user_from_cookie
from sqlalchemy import insert, select, delete, update
from command.models import command, member

router = APIRouter(
    prefix='/command',
    tags=['Command']
)


@router.get('/get_commands')
async def get_commands(offset: int = 0, limit: int = 100,
                       session: AsyncSession = Depends(get_async_session)):
    query = select(command).offset(offset).limit(offset + limit)
    result = await session.execute(query)
    return result.mappings().all()


@router.post('/{command_name}/del_command/', dependencies=[Depends(get_admin_status_from_cookie)])
async def del_command_by_name(command_name: str,
                              session: AsyncSession = Depends(get_async_session),
                              user_status: bool = Depends(get_admin_status_from_cookie)):
    if user_status:
        try:
            query = delete(command).where(command.c.name == command_name)
            await session.execute(query)
            await session.commit()
            return 'Delete command successful'
        except Exception as e:
            print(e)
            raise HTTPException(status_code=401, detail='Credentials not correct')
    else:
        raise HTTPException(status_code=401, detail='Unauthorized as superuser')


@router.get('/{command_name}')
async def get_command_by_name(command_name: str, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(command).where(command.c.name == command_name)
        result = await session.execute(query)
        return result.mappings().one_or_none()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail='Credentials not correct')


@router.post('/{command_name}/add_member', dependencies=[Depends(get_current_user_from_cookie)])
async def add_member(command_name: str,
                     lastname: str = Form(max_length=64),
                     name: str = Form(max_length=64),
                     surname: str = Form(max_length=64),
                     session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(command).where(command.c.name == command_name)
        result = await session.execute(query)
        command_id = result.mappings().one_or_none()['id']
        result = {'lastname': lastname,
                  'name': name,
                  'surname': surname,
                  'command_id': command_id}
        try:
            stmt = insert(member).values(**result)
            await session.execute(stmt)
            await session.commit()
            return 'Member added successfully'
        except Exception as e:
            print(e)
            raise HTTPException(status_code=401, detail='Credentials not correct')

    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail='Credentials not correct')


@router.post('/{command_name}/change_name', dependencies=[Depends(get_current_user_from_cookie)])
async def change_name(command_name: str,
                      new_name: str = Form(max_length=64),
                      session: AsyncSession = Depends(get_async_session)):
    try:
        stmt = update(command).where(command.name == command_name).values(name=new_name)
        await session.execute(stmt)
        await session.commit()
        return 'Command name updated successfully'
    except:
        raise HTTPException(status_code=401, detail='Credentials not correct')


@router.get('/{command_name}/members')
async def get_members(command_name: str, session: AsyncSession = Depends(get_async_session)):
    stmt = select(member).where(member.c.command_name == command_name)
    result = await session.execute(stmt)
    return result.mappings().all()
