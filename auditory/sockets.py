import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, delete, update

from database import get_async_session
from rating.routers import update_marks, get_marks
from auth.models import role, user
from security.secr import get_current_user_from_cookie

router = APIRouter(
    prefix="/auditory",
    tags=["auditory"]
)






