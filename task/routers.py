from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import insert, select, delete, update
from security.secr import get_admin_status_from_cookie, get_current_user_from_cookie
from task.models import task

router = APIRouter(
    prefix="/task",
    tags=["task"]
)


@router.post("/add_task", dependencies=[Depends(get_admin_status_from_cookie)])
async def add_task(number: int = Form(),
                   name: str = Form(),
                   description: str = Form(),
                   session: AsyncSession = Depends(get_async_session),
                   user_status: bool = Depends(get_admin_status_from_cookie)):
    if user_status:
        try:
            result = {'number': number,
                      'name': name,
                      'description': description}
            query = insert(task).values(**result)
            await session.execute(query)
            await session.commit()
            return 'Add task successful'
        except Exception as e:
            print(e)
            raise HTTPException(status_code=401, detail='Credentials not correct')
    else:
        raise HTTPException(status_code=401, detail='Unauthorized as superuser')


@router.post("/del_task", dependencies=[Depends(get_admin_status_from_cookie)])
async def add_task(number: int = Form(),
                   session: AsyncSession = Depends(get_async_session),
                   user_status: bool = Depends(get_admin_status_from_cookie)):
    if user_status:
        try:
            query = delete(task).where(task.c.number == number)
            await session.execute(query)
            await session.commit()
            return 'Delete task successful'
        except Exception as e:
            print(e)
            raise HTTPException(status_code=401, detail='Credentials not correct')
    else:
        raise HTTPException(status_code=401, detail='Unauthorized as superuser')


@router.get("/get_tasks")
async def get_tasks(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(task)
        result = await session.execute(query)
        return result.mappings().all()
    except:
        raise HTTPException(status_code=401, detail='Credentials not correct')