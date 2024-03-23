from sqlalchemy import MetaData, Table, Column, Integer, String, Text, ForeignKey, Float, JSON
from command.models import command, member

metadata = MetaData()

command_rating = Table(
    'command_rating',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('command_name', String, ForeignKey(command.c.name)),
    Column('place', Integer),
    Column('rating', Integer, default=0),
    Column('mark', Float, default=0),
)


personal_rating = Table(
    'personal_rating',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('member_id', Integer, ForeignKey(member.c.id)),
    Column('task_mark', JSON),
    Column('final_mark', Float, default=0),
)
