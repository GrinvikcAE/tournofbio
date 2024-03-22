from datetime import datetime
from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean
from sqlalchemy.orm import declarative_base


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
    Column('role_id', Integer, ForeignKey(role.c.id, ondelete='CASCADE'), default=6),
    Column('is_superuser', Boolean, default=False, nullable=False),
)


Base = declarative_base()


class Role(Base):
    __table__ = role


class User(Base):
    __table__ = user
