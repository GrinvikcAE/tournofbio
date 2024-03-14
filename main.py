from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from auth.models import role
from auth.routers import router as router_auth

app = FastAPI(
    title="Новосибирский ТЮБ",
)


@app.on_event("startup")
async def create_admin_user():
    try:
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


@app.get("", tags=['Main'])
async def root():
    return {"message": "Start complete"}
