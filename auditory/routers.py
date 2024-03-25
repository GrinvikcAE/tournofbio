from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from security.secr import COOKIE_NAME, ACCESS_TOKEN_EXPIRE_MINUTES
from security.secr import get_admin_status_from_cookie, get_current_user_from_cookie
from sqlalchemy import insert, select, delete, update
from command.models import command, member