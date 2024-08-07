from rest_framework import permissions
from todo_list_api.models import Task


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        block = Task.object.filter(user_id=request.user)

        return obj.user == request.user