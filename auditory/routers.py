from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse

from rating.models import marks
from security.secr import COOKIE_NAME, ACCESS_TOKEN_EXPIRE_MINUTES
from security.secr import get_admin_status_from_cookie, get_current_user_from_cookie
from sqlalchemy import insert, select, delete, update, and_
from auditory.models import auditory

# Column('id', Integer, primary_key=True, index=True),
# Column('number_of_action', Integer),
# Column('number_of_auditory', String),  # Possible in Assembly Hall
# Column('command', JSON),
# Column('master', Integer, ForeignKey(user.c.id)),
# Column('jury', JSON),
# Column('is_complete', Boolean, default=False)


router = APIRouter(
    prefix='/auditory',
    tags=['Auditory']
)


@router.get('/get_auditory')
async def get_auditory(
    offset: int = 0, limit: int = 100,
    session: AsyncSession = Depends(get_async_session),
    # cookie_user=Depends(get_current_user_from_cookie)
):
    query = select(auditory).order_by(auditory.c.number_of_action, auditory.c.number_of_auditory).offset(offset).limit(offset + limit)

    result = await session.execute(query)
    return result.mappings().all()


@router.get('/get_auditory_by_number')
async def get_auditory_by_number(
    number_of_auditory: str,
    action: int,
    current_user=Depends(get_current_user_from_cookie),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        if current_user is None:
            raise HTTPException(status_code=401, detail='Unauthorized')
        query = select(auditory).where(and_(auditory.c.number_of_auditory == number_of_auditory,
                                       auditory.c.number_of_action == action))
        result = await session.execute(query)
        return result.mappings().one_or_none()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail=f'Credentials not correct')


@router.post('/add_auditory', dependencies=[Depends(get_admin_status_from_cookie)])
async def add_auditory(
    aud_num: str,
    action: int,
    commands: str,
    jury: str,
    master: int,
    admin_status: bool = Depends(get_admin_status_from_cookie),
    session: AsyncSession = Depends(get_async_session)
):
    if admin_status:
        try:
            result = {
                'number_of_action': action,
                'number_of_auditory': aud_num,
                'command': {'commands': list(map(int, commands.split()))},
                'master': master,
                'jury': {'jury': list(map(int, jury.split()))},
                      }
            try:
                stmt = insert(auditory).values(**result)
                await session.execute(stmt)
                await session.commit()
                mrks = {'auditory': '1', 'action': '1', 'jury_mark': {}}
                stmt = insert(marks).values(mrks)
                await session.execute(stmt)
                return 'Successful'
            except Exception as e:
                print(e)
                raise HTTPException(status_code=401, detail='Credentials not correct')

        except Exception as e:
            print(e)
            raise HTTPException(status_code=401, detail='Credentials not correct')

    else:
        raise HTTPException(status_code=401, detail='Unauthorized as superuser')


@router.post('/del_auditory', dependencies=[Depends(get_admin_status_from_cookie)])
async def del_auditory(
    aud_num: str,
    action: int,
    admin_status: bool = Depends(get_admin_status_from_cookie),
    session: AsyncSession = Depends(get_async_session)
):
    if admin_status:
        try:
            stmt = delete(auditory).where(and_(auditory.c.number_of_auditory == aud_num,
                                               auditory.c.number_of_action == action))
            await session.execute(stmt)
            await session.commit()
            return f'Deleted'
        except Exception as e:
            print(e)
            raise HTTPException(status_code=401, detail='Credentials not correct')
    else:
        raise HTTPException(status_code=401, detail='Unauthorized as superuser')
