from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Task, TaskAccess
from .serializers import TaskSerializerCreate, TaskSerializerUpdate, TaskAccessSerializer, UserSerializer
from .views import TaskViewSet, TaskViewUpdate, TaskViewDelete, TaskAccessViewSet

class TaskModelTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

    def test_create_task(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'text': 'Test Task',
            'date': '2024-03-15T12:00:00Z'
        }
        response = self.client.post('/tasks/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['text'], 'Test Task')
        self.assertEqual(response.data['date'], '2024-03-15T12:00:00Z')
        self.assertEqual(response.data['user_id'], self.user1.id)

    def test_list_tasks(self):
        self.client.force_authenticate(user=self.user1)
        task = Task.objects.create(
            user_id=self.user1,
            text='Test Task',
            date='2024-03-15T12:00:00Z'
        )
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            {'id': task.id, 'text': 'Test Task', 'date': '2024-03-15T12:00:00Z'}, response.data
        )

    def test_update_task(self):
        self.client.force_authenticate(user=self.user1)
        task = Task.objects.create(
            user_id=self.user1,
            text='Test Task',
            date='2024-03-15T12:00:00Z'
        )
        data = {
            'text': 'Updated Task',
            'date': '2024-03-16T12:00:00Z'
        }
        response = self.client.put(f'/tasks/{task.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'Updated Task')
        self.assertEqual(response.data['date'], '2024-03-16T12:00:00Z')

    def test_delete_task(self):
        self.client.force_authenticate(user=self.user1)
        task = Task.objects.create(
            user_id=self.user1,
            text='Test Task',
            date='2024-03-15T12:00:00Z'
        )
        response = self.client.delete(f'/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_task_access(self):
        self.client.force_authenticate(user=self.user1)
        task = Task.objects.create(
            user_id=self.user1,
            text='Test Task',
            date='2024-03-15T12:00:00Z'
        )
        data = {
            'task': task.id,
            'user': self.user2.id,
        }
        response = self.client.post('/taskaccess/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['task'], task.id)
        self.assertEqual(response.data['user'], self.user2.id)

    def test_create_task_access_unauthorized(self):
        self.client.force_authenticate(user=self.user2)
        task = Task.objects.create(
            user_id=self.user1,
            text='Test Task',
            date='2024-03-15T12:00:00Z'
        )
        data = {
            'task': task.id,
            'user': self.user1.id,
        }
        response = self.client.post('/taskaccess/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'У пользователя user2 нет прав на предоставление доступа', str(response.data)
        )

    def test_update_task_access(self):
        self.client.force_authenticate(user=self.user1)
        task = Task.objects.create(
            user_id=self.user1,
            text='Test Task',
            date='2024-03-15T12:00:00Z'
        )
        task_access = TaskAccess.objects.create(
            task=task,
            user=self.user2,
        )
        data = {
            'can_read': False,
            'can_update': True
        }
        response = self.client.put(f'/taskaccess/{task_access.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['can_read'], False)
        self.assertEqual(response.data['can_update'], True)

    def test_update_task_access_unauthorized(self):
        self.client.force_authenticate(user=self.user2)
        task = Task.objects.create(
            user_id=self.user1,
            text='Test Task',
            date='2024-03-15T12:00:00Z'
        )
        task_access = TaskAccess.objects.create(
            task=task,
            user=self.user1,
        )
        data = {
            'can_read': False,
            'can_update': True
        }
        response = self.client.put(f'/taskaccess/{task_access.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(
            "У вас нет прав на изменение доступа к этой задаче.", str(response.data)
        )

    def test_delete_task_access(self):
        self.client.force_authenticate(user=self.user1)
        task = Task.objects.create(
            user_id=self.user1,
            text='Test Task',
            date='2024-03-15T12:00:00Z'
        )
        task_access = TaskAccess.objects.create(
            task=task,
            user=self.user2,
        )
        response = self.client.delete(f'/taskaccess/{task_access.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class TaskSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_task_serializer_create(self):
        data = {
            'text': 'Test Task',
            'date': '2024-03-15T12:00:00Z'
        }
        serializer = TaskSerializerCreate(data=data, context={'request': APIRequestFactory().get('/')})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['text'], 'Test Task')
        self.assertEqual(serializer.validated_data['date'], '2024-03-15T12:00:00Z')

    def test_task_serializer_update(self):
        task = Task.objects.create(
            user_id=self.user,
            text='Test Task',
            date='2024-03-15T12:00:00Z'
        )
        data = {
            'text': 'Updated Task',
            'date': '2024-03-16T12:00:00Z'
        }
        serializer = TaskSerializerUpdate(instance=task, data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['text'], 'Updated Task')
        self.assertEqual(serializer.validated_data['date'], '2024-03-16T12:00:00Z')

class TaskAccessSerializerTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.task = Task.objects.create(
            user_id=self.user1,
            text='Test Task',
            date='2024-03-15T12:00:00Z'
        )

    def test_task_access_serializer_valid(self):
        data = {
            'task': self.task.id,
            'user': self.user2.id,
        }
        serializer = TaskAccessSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['task'], self.task.id)
        self.assertEqual(serializer.validated_data['user'], self.user2.id)

    def test_task_access_serializer_invalid_task(self):
        data = {
            'task': 999, # Несуществующая задача
            'user': self.user2.id,
        }
        serializer = TaskAccessSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('task', serializer.errors)

    def test_task_access_serializer_invalid_user(self):
        data = {
            'task': self.task.id,
            'user': 999, # Несуществующий пользователь
        }
        serializer = TaskAccessSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('user', serializer.errors)

class UserSerializerTests(TestCase):

    def test_user_serializer_create(self):
        data = {
            'username': 'newuser',
            'password': 'password'
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['username'], 'newuser')
        self.assertEqual(serializer.validated_data['password'], 'password')
        user = serializer.save()
        self.assertTrue(User.objects.filter(pk=user.pk).exists())