from pydantic import EmailStr
from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import or_

from auditory.routers import get_auditory_by_number, get_auditory

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, delete, update

from auditory.sockets import managers
from database import get_async_session
from rating.routers import update_marks, get_marks
from auth.models import role, user
from security.secr import get_current_user_from_cookie

router = APIRouter(prefix='/root', tags=['Pages'])
templates = Jinja2Templates(directory='templates')


@router.api_route('', response_class=HTMLResponse, status_code=200, methods=["GET", "POST"])
async def get_root_page(
        request: Request,
        cookie_user=Depends(get_current_user_from_cookie),
        session: AsyncSession = Depends(get_async_session),
):
    if cookie_user is None or request.cookies == {}:
        return templates.TemplateResponse('root.html', {'request': request})
    else:
        return RedirectResponse(f'/{cookie_user["id"]}', status_code=302)
        # return await get_user(request=request, cookie_user=cookie_user, session=session)


@router.get('/{auditory}/{action}')
async def get_sockets_page(
        request: Request,
        auditory: str,
        action: int,
        cookie_user=Depends(get_current_user_from_cookie),
        session: AsyncSession = Depends(get_async_session),
):
    if cookie_user is None or request.cookies == {}:
        return await get_root_page(request, session=session)
    aud = await get_auditory_by_number(number_of_auditory=auditory, action=action, session=session)

    if cookie_user['role_id'] in (1, 2, 3, 4):
        managers.create_manager(auditory=auditory, action=action)
        stmt = select(user).where(or_(user.c.id in aud.jury['jury'], user.c.id == aud.master))
        result = await session.execute(stmt)
        jurys = result.mappings().all()
        return templates.TemplateResponse('auditory.html', {'request': request,
                                                            'auditory': aud,
                                                            'user': cookie_user,
                                                            'jurys': jurys
                                                            })


@router.api_route('/{user}', response_class=HTMLResponse, methods=["GET", "POST"])
async def get_user(
        request: Request,
        cookie_user=Depends(get_current_user_from_cookie),
        session: AsyncSession = Depends(get_async_session)
):
    if cookie_user is None or request.cookies == {}:
        return await get_root_page(request, session=session)
    if cookie_user['role_id'] in (1, 2, 3, 4, 5):
        aud_list = await get_auditory(session=session)
        closest_aud = aud_list[0] if len(aud_list) != 0 else {'number_of_auditory': '---',
                                                              'number_of_action': '---'}
        return templates.TemplateResponse('master.html',
                                          {
                                              'request': request,
                                              'cookie_user': cookie_user,
                                              'aud_list': aud_list,
                                              'closest_aud': closest_aud
                                          }
                                          )


# @router.api_route('/{user}/{command_name}', response_class=HTMLResponse, methods=["GET", "POST"])
# async def get_command(
#         command_name: str,
#         request: Request,
#         cookie_user=Depends(get_current_user_from_cookie),
#         session: AsyncSession = Depends(get_async_session)
# ):
#     if cookie_user is None:
#         return await get_root_page(request)
#     else:
#         members = await get_members(command_name, session)
#         return templates.TemplateResponse('command.html', {'request': request,
#                                                            'command_name': command_name,
#                                                            'members': members})
