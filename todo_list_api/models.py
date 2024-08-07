from django.db import models
from django.db.models.functions import Now
from django.contrib.auth.models import AbstractUser, User


# Create your models here.
# python manage.py makemigrations
# python manage.py migrate
# python manage.py shell
# from todo_list_api.models import TaskAccess

class Task(models.Model):
    user_id = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    text = models.CharField(max_length= 255, null=False, verbose_name='Текст')
    date = models.DateTimeField(null=True, blank=True, verbose_name='Дедлайн')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    shared_with = models.ManyToManyField(User, through='TaskAccess', related_name='shared_tasks', null=True, blank=True,)


    def __str__(self):
        return f'{self.text} {self.date}'


class TaskAccess(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # can_read = models.BooleanField(default=False)
    # can_update = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.task} {self.user}'