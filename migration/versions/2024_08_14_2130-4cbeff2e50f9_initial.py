"""initial

Revision ID: 4cbeff2e50f9
Revises: 
Create Date: 2024-08-14 21:30:12.997550

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4cbeff2e50f9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('permissions', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_role_id'), 'role', ['id'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lastname', sa.String(length=64), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('surname', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('commands_name', sa.JSON(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('ready_time', sa.JSON(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.create_table('command',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('tasks', sa.JSON(), nullable=True),
    sa.Column('registered_on', sa.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_command_id'), 'command', ['id'], unique=False)
    op.create_table('member',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lastname', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('surname', sa.String(length=64), nullable=True),
    sa.Column('tasks', sa.JSON(), nullable=True),
    sa.Column('command_name', sa.String(length=128), nullable=False),
    sa.ForeignKeyConstraint(['command_name'], ['command.name'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_member_id'), 'member', ['id'], unique=False)
    op.create_table('task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_id'), 'task', ['id'], unique=False)
    op.create_table('command_rating',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('command_name', sa.String(length=128), nullable=True),
    sa.Column('place', sa.Integer(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('mark', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['command_name'], ['command.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_command_rating_id'), 'command_rating', ['id'], unique=False)
    op.create_table('marks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('auditory', sa.String(), nullable=True),
    sa.Column('action', sa.String(), nullable=True),
    sa.Column('jury_mark', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_marks_id'), 'marks', ['id'], unique=False)
    op.create_table('personal_rating',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('task_mark', sa.JSON(), nullable=True),
    sa.Column('final_mark', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['member_id'], ['member.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_personal_rating_id'), 'personal_rating', ['id'], unique=False)
    op.create_table('auditory',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('number_of_action', sa.Integer(), nullable=True),
    sa.Column('number_of_auditory', sa.String(), nullable=True),
    sa.Column('command', sa.JSON(), nullable=True),
    sa.Column('master', sa.Integer(), nullable=True),
    sa.Column('jury', sa.JSON(), nullable=True),
    sa.Column('is_complete', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['master'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auditory_id'), 'auditory', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_auditory_id'), table_name='auditory')
    op.drop_table('auditory')
    op.drop_index(op.f('ix_personal_rating_id'), table_name='personal_rating')
    op.drop_table('personal_rating')
    op.drop_index(op.f('ix_marks_id'), table_name='marks')
    op.drop_table('marks')
    op.drop_index(op.f('ix_command_rating_id'), table_name='command_rating')
    op.drop_table('command_rating')
    op.drop_index(op.f('ix_task_id'), table_name='task')
    op.drop_table('task')
    op.drop_index(op.f('ix_member_id'), table_name='member')
    op.drop_table('member')
    op.drop_index(op.f('ix_command_id'), table_name='command')
    op.drop_table('command')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_role_id'), table_name='role')
    op.drop_table('role')
    # ### end Alembic commands ###
