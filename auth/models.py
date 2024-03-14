from datetime import datetime
from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean


metadata = MetaData()

role = Table(
    'role',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('name', String, nullable=False),
    Column('permissions', JSON, nullable=False)
)

user = Table(
    'user',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('lastname', String(64), nullable=True, unique=False),
    Column('name', String(64), nullable=True, unique=False),
    Column('surname', String(64), nullable=True, unique=False),
    Column('email', String(320), nullable=False, unique=True),
    Column('hashed_password', String(1024), nullable=False),
    Column('role_id', Integer, ForeignKey(role.c.id), default=6),
    Column('is_superuser', Boolean, default=False, nullable=False),
)

command = Table(
    'command',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('name', String(128), nullable=False, unique=True),
    Column('role_id', Integer, ForeignKey(role.c.id), default=5),
    Column('registered_on', TIMESTAMP, default=datetime.now),
)

member = Table(
    'member',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('lastname', String(64), nullable=False, unique=False),
    Column('name', String(64), nullable=False, unique=False),
    Column('surname', String(64), nullable=True, unique=False),
    Column('command', String(128), ForeignKey(command.c.name, ondelete='CASCADE'), nullable=False)
)
