from sqlalchemy import MetaData, Table, Column, Integer, String


metadata = MetaData()

task = Table(
    'task',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('number', Integer),
    Column('name', String(128), unique=False),
    Column('description', String())
)
