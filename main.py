from fastapi import FastAPI, Depends
from sqladmin import Admin
from fastapi.middleware.cors import CORSMiddleware
from database import engine, get_async_session, async_session_maker


from auth.models import role
from auth.routers import router as router_auth
from command.routers import router as router_command
from admin.routers import router as router_admin

from admin.views import RoleAdmin, UserAdmin, CommandAdmin, MemberAdmin
from admin.admin import AdminAuth

from config import JWT_SECRET

app = FastAPI(
    title="Новосибирский ТЮБ",
)
auth_back = AdminAuth(secret_key=JWT_SECRET, session=async_session_maker())

admin = Admin(app=app, engine=async_session_maker, authentication_backend=auth_back)


@app.on_event("startup")
async def add_role_to_db():
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
app.include_router(router_command)
app.include_router(router_admin)


@app.get("/", tags=['Main'])
async def root():
    return {"message": "Start complete"}
