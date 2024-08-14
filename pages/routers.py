from pydantic import EmailStr
from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from auth.models import user
from sqlalchemy import insert, select, delete, update
from command.models import command, member
from command.routers import get_members, get_command_by_name
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from database import get_async_session

from security.secr import get_current_user_from_cookie
from auditory.sockets import managers
from auditory.models import auditory
from auditory.routers import get_auditory_by_number, get_auditory

router = APIRouter(prefix='', tags=['Pages'])
templates = Jinja2Templates(directory='templates')


@router.api_route('/', response_class=HTMLResponse, status_code=200, methods=["GET", "POST"])
async def get_root_page(
        request: Request,
        cookie_user=Depends(get_current_user_from_cookie),
        session: AsyncSession = Depends(get_async_session),
):
    if cookie_user is None or request.cookies == {}:
        return templates.TemplateResponse('root.html', {'request': request})
    else:
        return await get_user(request=request, cookie_user=cookie_user, session=session)


@router.get('/auditory/{auditory}/{action}')
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

    if cookie_user['role_id'] in (1, 2):
        managers.create_manager(auditory=auditory, action=action)
        stmt = select(user).where(or_(user.c.id in aud.jury['jury'], user.c.id == aud.master))
        result = await session.execute(stmt)
        jurys = result.mappings().all()
        return templates.TemplateResponse('auditory.html', {'request': request,
                                                            'auditory': aud,
                                                            'user': cookie_user,
                                                            'jurys': jurys
                                                            })
    elif cookie_user['role_id'] == 3 and cookie_user['id'] == aud.master:
        managers.create_manager(auditory=auditory, action=action)
        stmt = select(user).where(or_(user.c.id in aud.jury['jury'], user.c.id == aud.master))
        result = await session.execute(stmt)
        jurys = result.mappings().all()
        return templates.TemplateResponse('auditory.html', {'request': request,
                                                            'auditory': aud,
                                                            'user': cookie_user,
                                                            'jurys': jurys})
    elif cookie_user['role_id'] == 4 and cookie_user['id'] in aud.jury['jury']:
        managers.create_manager(auditory=auditory, action=action)
        return templates.TemplateResponse('auditory.html', {'request': request,
                                                            'auditory': aud,
                                                            'user': cookie_user, })
    else:
        return templates.TemplateResponse('user.html', {'request': request, 'cookie_user': cookie_user})


@router.api_route('/{user}', response_class=HTMLResponse, methods=["GET", "POST"])
async def get_user(
        request: Request,
        cookie_user=Depends(get_current_user_from_cookie),
        session: AsyncSession = Depends(get_async_session)
):
    if cookie_user is None or request.cookies == {}:
        return await get_root_page(request, session=session)
    if cookie_user['role_id'] in (1, 2):
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
    elif cookie_user['role_id'] in (3, 4):
        aud_list = await get_auditory(session=session)
        personal_aud = []
        closest_aud = aud_list[0] if len(aud_list) != 0 else {'number_of_auditory': '---',
                                                              'number_of_action': '---'}

        for aud in aud_list:
            if cookie_user['id'] == aud['master'] or cookie_user['id'] in aud['jury']['jury']:
                personal_aud.append(aud)
        if len(personal_aud) != 0:
            for aud in personal_aud:
                if not aud['is_complete']:
                    closest_aud = aud
                    break

        return templates.TemplateResponse('master.html',
                                          {
                                              'request': request,
                                              'cookie_user': cookie_user,
                                              'aud_list': personal_aud,
                                              'closest_aud': closest_aud
                                          }
                                          )

    # if cookie_user['role_id'] == 5:
    #     return await get_command(command_name=cookie_user['commands_name'][0]['commands'][0], request=request)
    # else:
    #     return templates.TemplateResponse('user.html', {'request': request, 'cookie_user': cookie_user})


@router.api_route('/{user}/{command_name}', response_class=HTMLResponse, methods=["GET", "POST"])
async def get_command(
        command_name: str,
        request: Request,
        cookie_user=Depends(get_current_user_from_cookie),
        session: AsyncSession = Depends(get_async_session)
):
    if cookie_user is None:
        return await get_root_page(request)
    else:
        members = await get_members(command_name, session)
        return templates.TemplateResponse('command.html', {'request': request,
                                                           'command_name': command_name,
                                                           'members': members})
