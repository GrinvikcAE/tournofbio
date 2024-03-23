from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import insert, select, delete, update
from security.secr import get_admin_status_from_cookie, get_current_user_from_cookie
from rating.models import personal_rating, command_rating

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
