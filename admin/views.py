from sqladmin import ModelView
from auth.models import Role, User
from command.models import Command, Member


class RoleAdmin(ModelView, model=Role):
    column_list = '__all__'
    details_template = "custom_details.html"


class UserAdmin(ModelView, model=User):
    column_list = [User.name, User.lastname, User.email,]
    column_searchable_list = [User.name, User.lastname, User.email,]
    column_sortable_list = [User.id]


class CommandAdmin(ModelView, model=Command):
    column_list = '__all__'


class MemberAdmin(ModelView, model=Member):
    column_list = '__all__'
