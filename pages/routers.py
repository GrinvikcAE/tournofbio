from pydantic import EmailStr
from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from auth.models import user
from sqlalchemy import insert, select, delete, update
from command.models import command, member
from command.routers import get_members, get_command_by_name

from security.secr import get_current_user_from_cookie

router = APIRouter(prefix='', tags=['Pages'])
templates = Jinja2Templates(directory='templates')


@router.api_route('/', response_class=HTMLResponse, status_code=200, methods=["GET", "POST"])
async def get_root_page(request: Request):
    return templates.TemplateResponse('root.html', {'request': request})


@router.api_route('/{user_id}', response_class=HTMLResponse, methods=["GET", "POST"])
async def get_user(request: Request,
                   cookie_user=Depends(get_current_user_from_cookie)):
    if cookie_user is None:
        return await get_root_page(request)
    if cookie_user['role_id'] == 5:
        print(cookie_user['commands_name'][0]['commands'][0])
        return await get_command(command_name=cookie_user['commands_name'][0]['commands'][0], request=request)
    else:
        return templates.TemplateResponse('user.html', {'request': request, 'cookie_user': cookie_user})


@router.api_route('/{command_name}', response_class=HTMLResponse, methods=["GET", "POST"])
async def get_command(command_name: str,
                      request: Request,
                      cookie_user=Depends(get_current_user_from_cookie)):
    if cookie_user is None:
        return await get_root_page(request)
    else:
        members = await get_members(command_name)
        return templates.TemplateResponse('command.html', {'request': request, 'members': members})
