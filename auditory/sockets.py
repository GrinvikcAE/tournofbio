import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from rating.routers import update_marks, get_marks

router = APIRouter(
    prefix="/auditory",
    tags=["auditory"]
)


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


@router.websocket("/ws/{auditory}/{action}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, auditory: str, action: int, client_id: int,
                             session: AsyncSession = Depends(get_async_session)):
    manager = managers.active_managers[(auditory, action)]
    new_marks = await get_marks(auditory=auditory, action=str(action), session=session)
    new_marks = new_marks['jury_mark']
    marks.aud_dict = new_marks
    print(marks.aud_dict)

    marks.add_auditory(auditory=auditory, action=str(action))
    marks.add_jury(auditory=auditory, action=str(action), jury=str(client_id))
    await manager.connect(websocket=websocket, user_id=client_id)

    active_user = [ws['user_id'] for ws in manager.active_connections]
    result = json.dumps(marks.get_results(auditory=auditory, action=str(action)))

    message = json.dumps(
        {'client_id': client_id,
         'data': None,
         'active_users': active_user,
         'marks': json.dumps(new_marks),
         'result': result}
    )
    # await manager.send_personal_message(message, websocket=websocket)

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
            new_marks = new_marks['jury_mark']
            marks.aud_dict = new_marks
            print(marks.aud_dict)
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
        # await manager.broadcast(f"Client #{client_id} left the chat")

