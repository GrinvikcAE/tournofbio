from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import insert, select, delete, update, and_
from security.secr import get_admin_status_from_cookie, get_current_user_from_cookie
from rating.models import personal_rating, command_rating, marks

router = APIRouter(
    prefix="/rating",
    tags=["Rating"]
)


@router.get("/get_personal_rating")
async def get_personal_rating(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(personal_rating)
        result = await session.execute(query)
        return result.mappings().all()
    except:
        raise HTTPException(status_code=401, detail='Credentials not correct')


@router.get("/get_command_rating")
async def get_command_rating(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(command_rating)
        result = await session.execute(query)
        return result.mappings().all()
    except:
        raise HTTPException(status_code=401, detail='Credentials not correct')


@router.get("/get_marks/{auditory}/{action}")
async def get_marks(
        auditory: str,
        action: str,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        query = select(marks).where(and_(marks.c.auditory == auditory, marks.c.action == action))
        result = await session.execute(query)
        return result.mappings().one_or_none()
    except:
        raise HTTPException(status_code=401, detail='Credentials not correct')


@router.post("/get_marks/{auditory}/{action}")
async def update_marks(
        auditory: str,
        action: str,
        new_marks: dict,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = update(marks).where(and_(marks.c.auditory == auditory,
                                        marks.c.action == action)).values({'jury_mark': new_marks})
        await session.execute(stmt)
        await session.commit()
    except:
        raise HTTPException(status_code=401, detail='Credentials not correct')
