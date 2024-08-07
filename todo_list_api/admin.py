from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from todo_list_api.models import Task, User, TaskAccess
# Register your models here.
admin.site.register(Task)
admin.site.register(TaskAccess)