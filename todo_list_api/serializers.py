from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Task, TaskAccess
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class UserSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user

    class Meta:
        model = UserModel
        fields = "__all__"




#Переобразует данные из БД в JSON формат и наоборот
#Этот сериализатор работает толко на добавление
class TaskSerializerCreate(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Task
        fields = "__all__"


    def create(self, validated_data):
        print(f'Creating Task with data: {validated_data}')
        return Task.objects.create( **validated_data )

# Этот серилизатор работает только на обновление
class TaskSerializerUpdate(serializers.ModelSerializer):
    user_id = serializers.CharField(required=False) #Делает поле user_id не обязательным в запросе

    class Meta:
        model = Task
        fields = "__all__"

    #Устанваливаем поле user_id по умлочанию тем же значением, что положили при создании
    def update(self, instance, validated_data):
        # Удаляем поле внешнего ключа из validated_data, чтобы не оверрайдить его
        validated_data.pop('user_id', None)  # замените на имя вашего поля внешнего ключа
        return super().update(instance, validated_data)



class TaskAccessSerializer(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all())

    class Meta:
        model = TaskAccess
        fields = '__all__'




    # text = serializers.CharField(max_length=255)
    # date = serializers.DateTimeField()
    # date_create = serializers.DateTimeField(read_only=True)
    #
    # def create(self, validated_data):
    #     return TaskCreate.objects.create(**validated_data)
    #
    # def update(self, instance, validated_data):
    #     instance.text = validated_data.get("text", instance.text)
    #     instance.date = validated_data.get("date", instance.date)
    #     instance.date_create = validated_data.get("date_create", instance.date_create)
    #     instance.save()
    #     return instance




