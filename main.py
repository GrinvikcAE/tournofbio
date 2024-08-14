from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin
from fastapi.middleware.cors import CORSMiddleware
from database import engine, async_session_maker

from auth.models import role, user
from auth.routers import router as router_auth
from command.routers import router as router_command
from rating.models import marks
from task.routers import router as router_task
from rating.routers import router as router_rating
from user.routers import router as router_user
from auditory.sockets import router as router_auditory_sockets
from auditory.routers import router as router_auditory

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


# @app.on_event("startup")
# async def add_on_startup():
    # try:
    #     admin.add_view(RoleAdmin)
    #     admin.add_view(UserAdmin)
    #     admin.add_view(CommandAdmin)
    #     admin.add_view(MemberAdmin)
    #     async with engine.begin() as conn:
    #         roles = [{'id': 1, 'name': 'super-admin', 'permissions': []},
    #                  {'id': 2, 'name': 'admin', 'permissions': []},
    #                  {'id': 3, 'name': 'master', 'permissions': []},
    #                  {'id': 4, 'name': 'jury', 'permissions': []},
    #                  {'id': 5, 'name': 'command', 'permissions': []},
    #                  {'id': 6, 'name': 'nobody', 'permissions': []}]
    #         try:
    #             await conn.execute(role.insert(), roles)
    #         except Exception as e:
    #             print(e)
    #     await engine.dispose()
    # except Exception as e:
    #     print(e)
    # try:
    #     users = [
    #         {'email': ADMIN,
    #          'hashed_password': await get_password_hash(PASWD),
    #          'is_superuser': True, 'role_id': 1},
    #         {'email': 'Баймак',
    #          'lastname': 'Баймак',
    #          'name': 'Татьяна',
    #          'hashed_password': await get_password_hash('nTtEcB2j'),
    #          'is_superuser': False, 'role_id': 4},
    #         {'email': 'Андреюшкова',
    #          'lastname': 'Андреюшкова',
    #          'name': 'Дарья',
    #          'hashed_password': await get_password_hash('2inQoYYn'),
    #          'is_superuser': False, 'role_id': 4},
    #         {'email': 'Баласов',
    #          'lastname': 'Баласов',
    #          'name': 'Сергей',
    #          'hashed_password': await get_password_hash('TFkfD7sm'),
    #          'is_superuser': False, 'role_id': 4},
    #         {'email': 'Линков',
    #          'lastname': 'Линков',
    #          'name': 'Никита',
    #          'hashed_password': await get_password_hash('k35QESi5'),
    #          'is_superuser': False, 'role_id': 4},
    #         {'email': 'Маршалкин',
    #          'lastname': 'Маршалкин',
    #          'name': 'Леонид',
    #          'hashed_password': await get_password_hash('24YXwVEC'),
    #          'is_superuser': False, 'role_id': 4},
    #         {'email': 'Григорьева',
    #          'lastname': 'Григорьева',
    #          'name': 'Елена',
    #          'hashed_password': await get_password_hash('4cBXO6uG'),
    #          'is_superuser': False, 'role_id': 4},
    #         {'email': 'Воронина',
    #          'lastname': 'Воронина',
    #          'name': 'Елена',
    #          'surname': 'Николаевна',
    #          'hashed_password': await get_password_hash('wZv6basQ'),
    #          'is_superuser': False, 'role_id': 4},
    #         {'email': 'Тепер',
    #          'lastname': 'Тепер',
    #          'name': 'София',
    #          'hashed_password': await get_password_hash('9AS4yU22'),
    #          'is_superuser': False, 'role_id': 4},
    #         {'email': 'Волошина',
    #          'lastname': 'Волошина',
    #          'name': 'Марина',
    #          'surname': 'Александровна',
    #          'hashed_password': await get_password_hash('uCT14G5p'),
    #          'is_superuser': False, 'role_id': 4},
    #         {'email': 'Шефер',
    #          'lastname': 'Шефер',
    #          'name': 'Алексей',
    #          'hashed_password': await get_password_hash('7dpQVztM'),
    #          'is_superuser': False, 'role_id': 4},
    #         {'email': 'Жданков',
    #          'lastname': 'Жданков',
    #          'name': 'Илья',
    #          'surname': 'Васильевич',
    #          'hashed_password': await get_password_hash('HuinyaIsPodKonya'),
    #          'is_superuser': False, 'role_id': 4},
    #         {'email': 'Держалова',
    #          'lastname': 'Держалова',
    #          'name': 'Алина',
    #          'hashed_password': await get_password_hash('Mebm5BY3'),
    #          'is_superuser': False, 'role_id': 3},
    #         {'email': 'Сидоренко',
    #          'lastname': 'Сидоренко',
    #          'name': 'Александра',
    #          'hashed_password': await get_password_hash('fG673trY'),
    #          'is_superuser': False, 'role_id': 4},
    #         {'email': 'Яковлева',
    #          'lastname': 'Яковлева',
    #          'name': 'Софья',
    #          'hashed_password': await get_password_hash('Fg45jpR3'),
    #          'is_superuser': False, 'role_id': 4},
    #         {'email': 'Ломова',
    #          'lastname': 'Ломова',
    #          'name': 'Лариса',
    #          'surname': 'Анатольевна',
    #          'hashed_password': await get_password_hash('HD379tYA'),
    #          'is_superuser': False, 'role_id': 4},
    #         {'email': 'Шин',
    #          'lastname': 'Шин',
    #          'name': 'Елизавета',
    #          'hashed_password': await get_password_hash('ZabiliNaTebya'),
    #          'is_superuser': False, 'role_id': 4},
    #         {'email': 'Электровеник',
    #          'hashed_password': await get_password_hash('690Su67H'),
    #          'is_superuser': False, 'role_id': 5},
    #         {'email': 'Овощи',
    #          'hashed_password': await get_password_hash('56Dsh54X'),
    #          'is_superuser': False, 'role_id': 5},
    #         {'email': 'НеТотПрайд',
    #          'hashed_password': await get_password_hash('Ft4wS38'),
    #          'is_superuser': False, 'role_id': 5},
    #         {'email': 'БезСмысла',
    #          'hashed_password': await get_password_hash('CV72ed12'),
    #          'is_superuser': False, 'role_id': 5},
    #
    #     ]
    #
    #     async with engine.begin() as conn:
    #         try:
    #             await conn.execute(user.insert(), users)
    #         except Exception as e:
    #             print(e)
    #     await engine.dispose()
    # except Exception as e:
    #     print(e)

    # try:
    #     async with engine.begin() as conn:
    #         mrks = [{'auditory': '1', 'action': '1', 'jury_mark': {}}]
    #         try:
    #             await conn.execute(marks.insert(), mrks)
    #         except Exception as e:
    #             print(e)
    #     await engine.dispose()
    # except Exception as e:
    #     print(e)


app.mount('/static', StaticFiles(directory='static'), name='static')

origins = [
    'http://localhost:8000',
    'https://localhost:8000',
    'http://127.0.0.1:8000',
    'https://127.0.0.1:8000',
    'https://0.0.0.0:8000',
    'http://0.0.0.0:8000',
    'https://tournofbio.onrender.com',
    'http://tournofbio.onrender.com',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    max_age=1000,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Access-Control-Allow-Headers", "Access-Control-Allow-Methods",
                   "Authorization", "Set-Cookie", "Cross-Origin", 'Access-Control-Request-Method'
                   ]
)

app.include_router(router_auth)
app.include_router(router_user)
app.include_router(router_command)
app.include_router(router_auditory_sockets)
app.include_router(router_auditory)

app.include_router(router_task)
app.include_router(router_rating)

app.include_router(router_pages)

app.include_router(router_admin)
