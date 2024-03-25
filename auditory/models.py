from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean
from auth.models import user

metadata = MetaData()

auditory = Table(
    'auditory',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('number_of_action', Integer),
    Column('number_of_auditory', String),  # Possible in Assembly Hall
    Column('command', JSON),
    Column('master', Integer, ForeignKey(user.c.id)),
    Column('jury', JSON),
    Column('is_complete', Boolean, default=False)
)
