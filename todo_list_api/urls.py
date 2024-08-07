from django.urls import path, include
from requests import auth
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import TaskViewSet, CreateUserView, TaskViewUpdate, TaskViewDelete, TaskAccessViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename= 'task')
router.register(r'task_access', TaskAccessViewSet, basename= 'task-access')
router.register(r'create_user', CreateUserView)

urlpatterns = [
    path('', include(router.urls)),
    path('tasks/<int:pk>/', TaskViewUpdate.as_view()),
    path('tasks_delete/<int:pk>/', TaskViewDelete.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]