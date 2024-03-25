from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin
from fastapi.middleware.cors import CORSMiddleware
from database import engine, async_session_maker

from auth.models import role, user
from auth.routers import router as router_auth
from command.routers import router as router_command
from task.routers import router as router_task
from rating.routers import router as router_rating
from user.routers import router as router_user

from admin.routers import router as router_admin

from pages.routers import router as router_pages

from admin.views import RoleAdmin, UserAdmin, CommandAdmin, MemberAdmin
from admin.admin import AdminAuth

from config import JWT_SECRET, ADMIN, PASWD
from security.secr import get_password_hash

app = FastAPI(
    title="Новосибирский ТЮБ",
    redoc_url=None,
)
auth_back = AdminAuth(secret_key=JWT_SECRET, session=async_session_maker())

admin = Admin(app=app, engine=async_session_maker, authentication_backend=auth_back)


@app.on_event("startup")
async def add_on_startup():
    try:
        admin.add_view(RoleAdmin)
        admin.add_view(UserAdmin)
        admin.add_view(CommandAdmin)
        admin.add_view(MemberAdmin)
        async with engine.begin() as conn:
            roles = [{'id': 1, 'name': 'super-admin', 'permissions': []},
                     {'id': 2, 'name': 'admin', 'permissions': []},
                     {'id': 3, 'name': 'master', 'permissions': []},
                     {'id': 4, 'name': 'jury', 'permissions': []},
                     {'id': 5, 'name': 'command', 'permissions': []},
                     {'id': 6, 'name': 'nobody', 'permissions': []}]
            try:
                await conn.execute(role.insert(), roles)
            except Exception as e:
                print(e)
        await engine.dispose()
    except Exception as e:
        print(e)
    try:
        async with engine.begin() as conn:
            users = [{'email': ADMIN, 'hashed_password': await get_password_hash(PASWD),
                      'is_superuser': True, 'role_id': 1}]
            try:
                await conn.execute(user.insert(), users)
            except Exception as e:
                print(e)
        await engine.dispose()
    except Exception as e:
        print(e)

app.mount('/static', StaticFiles(directory='static'), name='static')


origins = [
    'http://localhost:8000',
    'https://localhost:8000',
    'http://127.0.0.1:8000',
    'https://127.0.0.1:8000',
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    max_age=10,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Access-Control-Allow-Headers", "Access-Control-Allow-Methods",
                   "Authorization", "Set-Cookie", "Cross-Origin", 'Access-Control-Request-Method']
)

app.include_router(router_auth)
app.include_router(router_user)
app.include_router(router_command)
app.include_router(router_task)
app.include_router(router_rating)

app.include_router(router_pages)

app.include_router(router_admin)
