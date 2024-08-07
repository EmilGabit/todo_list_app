from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, \
    RetrieveDestroyAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from todo_list_api.models import Task, TaskAccess
from todo_list_api.serializers import TaskSerializerCreate, UserSerializer, TaskAccessSerializer, TaskSerializerUpdate


class CreateUserView(CreateModelMixin, GenericViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer





#Возвращает задачи из БД GET запрос с фильтрацией, Добавляет данные в БД POST
class TaskViewSet(ListCreateAPIView, GenericViewSet):
    serializer_class = TaskSerializerCreate
    permission_classes = [IsAuthenticated]

    #Филтруем пользователей, которм доступны задачи
    def get_queryset(self):
        return Task.objects.filter(user_id = self.request.user) | Task.objects.filter(shared_with=self.request.user)


#Обновляет запись PUT
class TaskViewUpdate(RetrieveUpdateAPIView):
    serializer_class = TaskSerializerUpdate
    permission_classes = [IsAuthenticated]

    # Филтруем пользователей, котором доступно обновление
    def get_queryset(self):
        return (Task.objects.filter(user_id = self.request.user) | Task.objects.filter(shared_with=self.request.user))


#Удаляет запись DELETE
class TaskViewDelete(RetrieveDestroyAPIView):
    serializer_class = TaskSerializerUpdate
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user_id=self.request.user)


# Разграничение прав доступа
class TaskAccessViewSet(ModelViewSet):
    serializer_class = TaskAccessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TaskAccess.objects.all()


    def perform_create(self, serializer):
        user_created = Task.objects.filter(pk = self.request.data['task']).first().user_id
        if user_created != self.request.user:
            raise ValidationError(f'У пользователя {self.request.user} нет прав на предоставление доступа')
        else:
            task = TaskAccess.objects.filter(task=self.request.data['task'])
            user = TaskAccess.objects.filter(task=self.request.data['user'])
            if task and user:
                raise ValidationError(f'В таблице уже есть эта задача, воспользуйтесь методом PUT')
            else:
                serializer.save()


    def perform_update(self, serializer):
        users = Task.objects.filter(pk=self.request.data['task']).first().user_id
        if users != self.request.user:
            raise PermissionDenied(f"У вас нет прав на изменение доступа к этой задаче.")
        else:
            return TaskAccess.objects.all()


