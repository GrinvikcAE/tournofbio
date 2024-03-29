from datetime import datetime
from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.orm import declarative_base


metadata = MetaData()

command = Table(
    'command',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('name', String(128), nullable=False, unique=True),
    Column('tasks', JSON),
    Column('registered_on', TIMESTAMP, default=datetime.now),
)

member = Table(
    'member',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('lastname', String(64), nullable=False, unique=False),
    Column('name', String(64), nullable=False, unique=False),
    Column('surname', String(64), nullable=True, unique=False),
    Column('tasks', JSON, nullable=True, unique=False),
    Column('command_name', String(128), ForeignKey(command.c.name, ondelete='CASCADE'), nullable=False)
)


Base = declarative_base()


class Command(Base):
    __table__ = command


class Member(Base):
    __table__ = member
