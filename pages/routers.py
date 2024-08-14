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

from database import get_async_session
from rating.routers import update_marks, get_marks
from auth.models import role, user
from security.secr import get_current_user_from_cookie

router = APIRouter(prefix='', tags=['Pages'])
templates = Jinja2Templates(directory='templates')


@router.api_route('/root', response_class=HTMLResponse, status_code=200, methods=["GET", "POST"])
async def get_root_page(
        request: Request,
        cookie_user=Depends(get_current_user_from_cookie),
        session: AsyncSession = Depends(get_async_session),
):
    if cookie_user is None or request.cookies == {}:
        return templates.TemplateResponse('root.html', {'request': request})
    else:
        return RedirectResponse(f'/root/{cookie_user["id"]}', status_code=302)
        # return await get_user(request=request, cookie_user=cookie_user, session=session)


@router.get('/root/{auditory}/{action}')
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


@router.api_route('/root/{user}', response_class=HTMLResponse, methods=["GET", "POST"])
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
    # elif cookie_user['role_id'] in (3, 4):
    #     aud_list = await get_auditory(session=session)
    #     personal_aud = []
    #     closest_aud = aud_list[0] if len(aud_list) != 0 else {'number_of_auditory': '---',
    #                                                           'number_of_action': '---'}
    #
    #     for aud in aud_list:
    #         if cookie_user['id'] == aud['master'] or cookie_user['id'] in aud['jury']['jury']:
    #             personal_aud.append(aud)
    #     if len(personal_aud) != 0:
    #         for aud in personal_aud:
    #             if not aud['is_complete']:
    #                 closest_aud = aud
    #                 break
    #
    #     return templates.TemplateResponse('master.html',
    #                                       {
    #                                           'request': request,
    #                                           'cookie_user': cookie_user,
    #                                           'aud_list': personal_aud,
    #                                           'closest_aud': closest_aud
    #                                       }
    #                                       )

    # if cookie_user['role_id'] == 5:
    #     return await get_command(command_name=cookie_user['commands_name'][0]['commands'][0], request=request)
    # else:
    #     return templates.TemplateResponse('user.html', {'request': request, 'cookie_user': cookie_user})


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
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[dict[str: WebSocket, str: int]] = []

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections.append({'websocket': websocket, 'user_id': user_id})

    def disconnect(self, websocket: WebSocket, user_id: int):
        self.active_connections.remove({'websocket': websocket, 'user_id': user_id})

    async def send_personal_message(self, message: json, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection['websocket'].send_text(message)


class Managers:
    def __init__(self):
        self.active_managers: dict[tuple, ConnectionManager] = dict()

    def create_manager(self, auditory: str, action: int):
        if (auditory, action) not in self.active_managers:
            manager = ConnectionManager()
            self.active_managers[(auditory, action)] = manager

    def delete_manager(self, auditory: str, action: int):
        self.active_managers.pop((auditory, action), None)


class Marks:
    def __init__(self):
        self.aud_dict: dict[str, dict] = {}

    def add_auditory(self, auditory: str, action: str):
        if auditory not in self.aud_dict:
            self.aud_dict[auditory] = {}

        if action not in self.aud_dict[auditory]:
            self.aud_dict[auditory][action] = {}

    def add_jury(self, auditory: str, action: str, jury: str):
        if jury not in self.aud_dict[auditory][action]:
            self.aud_dict[auditory][action][jury] = {'act1': {'d1': 0,
                                                              'd2': 0,
                                                              'd3': 0,
                                                              'o1': 0,
                                                              'o2': 0,
                                                              'r': 0},
                                                     'act2': {'d1': 0,
                                                              'd2': 0,
                                                              'd3': 0,
                                                              'o1': 0,
                                                              'o2': 0,
                                                              'r': 0},
                                                     'act3': {'d1': 0,
                                                              'd2': 0,
                                                              'd3': 0,
                                                              'o1': 0,
                                                              'o2': 0,
                                                              'r': 0},
                                                     'act4': {'d1': 0,
                                                              'd2': 0,
                                                              'd3': 0,
                                                              'o1': 0,
                                                              'o2': 0,
                                                              'r': 0},
                                                     }

    def get_results(self, auditory: str, action: str):
        results = {'act1': [0, 0, 0], 'act2': [0, 0, 0], 'act3': [0, 0, 0], 'act4': [0, 0, 0]}
        for jury in self.aud_dict[auditory][action]:
            for act in results:
                results[act][0] += self.aud_dict[auditory][action][jury][act]['d1'] + \
                                   self.aud_dict[auditory][action][jury][act]['d2'] + \
                                   self.aud_dict[auditory][action][jury][act]['d3']
                results[act][1] += self.aud_dict[auditory][action][jury][act]['o1'] + \
                                   self.aud_dict[auditory][action][jury][act]['o2']
                results[act][2] += self.aud_dict[auditory][action][jury][act]['r']

        for act in results:
            results[act][0] = round(results[act][0] / len(self.aud_dict[auditory][action]), 2)
            results[act][1] = round(results[act][1] / len(self.aud_dict[auditory][action]), 2)
            results[act][2] = round(results[act][2] / len(self.aud_dict[auditory][action]), 2)
        return results

    def update_mark(self, auditory: str, action: str, jury: str, act: list, mark: str):
        if mark != '0':
            mark2value = {'5+': 100, '5': 85, '5-': 70, '4+': 60, '4': 50, '4-': 40, '3+': 30, '3': 25, '3-': 20, '0': 0}
            self.aud_dict[auditory][action][jury][act[0]][act[1]] = mark2value[mark]


managers = Managers()
marks = Marks()


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket, auditory: str = '1', action: int = 1,
                             session: AsyncSession = Depends(get_async_session),
                             cookie_user=Depends(get_current_user_from_cookie)):
    client_id = cookie_user['id']
    manager = managers.active_managers[(auditory, action)]
    new_marks = await get_marks(auditory=auditory, action=str(action), session=session)
    if new_marks is not None:
        new_marks = new_marks['jury_mark']
        marks.aud_dict = new_marks

    marks.add_auditory(auditory=auditory, action=str(action))
    marks.add_jury(auditory=auditory, action=str(action), jury=str(client_id))
    print(websocket, auditory, action, client_id)
    await manager.connect(websocket=websocket, user_id=client_id)
    print('connected')

    active_user = [ws['user_id'] for ws in manager.active_connections]
    result = json.dumps(marks.get_results(auditory=auditory, action=str(action)))
    message = json.dumps(
        {'client_id': client_id,
         'data': None,
         'active_users': active_user,
         'marks': json.dumps(new_marks),
         'result': result}
    )

    await manager.broadcast(message)

    try:
        while True:
            data = await websocket.receive_text()
            jury_id, act, mark = data.split('|')
            act = act.split('-')

            marks.update_mark(auditory=auditory, action=str(action), jury=str(client_id), act=act, mark=mark)
            await update_marks(auditory=auditory,
                               action=str(action),
                               new_marks=marks.aud_dict,
                               session=session)

            new_marks = await get_marks(auditory=auditory, action=str(action), session=session)
            if new_marks is not None:
                new_marks = new_marks['jury_mark']
                marks.aud_dict = new_marks

            result = json.dumps(marks.get_results(auditory=auditory, action=str(action)))

            message = json.dumps(
                {'client_id': client_id,
                 'data': data,
                 'active_users': active_user,
                 'marks': json.dumps(marks.aud_dict),
                 'result': result}
            )
            await manager.broadcast(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket=websocket, user_id=client_id)