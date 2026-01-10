from django.contrib.auth.hashers import make_password
from rest_framework.generics import *
from rest_framework.views import *
from .models import *
from .serializer import Serializer
from pydantic import BaseModel, EmailStr, Field, ConfigDict
import hashlib

def hash_id(id_user):
    data = f"{id_user}".encode('utf-8')
    hasher = hashlib.sha256()
    hasher.update(data)
    hashed_data = hasher.hexdigest()
    return hashed_data

class RegistrationView(CreateAPIView):
    serializer_class = Serializer

    def post(self, request):
        #получаем данные пользовтеля
        response_login = request.data.get('login')
        response_email = request.data.get('email')
        response_number = request.data.get('number')
        response_password = request.data.get('password')

        #Валидация (проверка) данных
        class Validate(BaseModel):
            login:str = Field(min_length=3,max_length=40)
            email:EmailStr = Field(min_length=3,max_length=50)
            number:str = Field(min_length=6, max_length=12)
            password:str = Field(min_length=4,max_length=40)
            model_config=ConfigDict(extra='forbid') 
        Validate(**request.data)

        #Хеширование поролей
        response_password_hash = make_password(response_password)
        
        #Запись данных в БД
        Models.objects.create(
            login=response_login, 
            email=response_email,
            number=response_number, 
            password=response_password_hash
            )
           
        return Response({"post":200})
        
        

class LoginView(APIView):                                                                                           
    def post(self, request):
        #получаем данные пользовтеля                                                                                        
        response_login = request.data.get('login')                                                                  
        response_password = request.data.get('password')

        #Проверка данных
        class Validate(BaseModel):
            login:str=Field(min_length=3,max_length=40)
            password:str=Field(min_length=4,max_length=40)
            model_config=ConfigDict(extra='forbid')
        Validate(**request.data)

        #Проверка пользователя
        try:
            queryset_login =  Models.objects.get(login=response_login)
        except Models.DoesNotExist:
            raise Http404({
                'meaning':'Такова пользователя несуществует',
                'status':status.HTTP_404_NOT_FOUND
                           })
        
        #проверка пороли
        if queryset_login.check_password(response_password):
            #если пароль правельный берем данные их бд (номер,id пользователя)
            user_data = Models.objects.filter(login=response_login).values('id', 'number').first()
            queryset_login.save()

            return Response({
                'id_users':hash_id(user_data['id']),
                'login': response_login,
                'number':user_data['number'],
                'status':status.HTTP_201_CREATED
                })
        
        #Если пороль не верный
        raise Http404({
                'meaning':'Неверный пороль',
                'status':status.HTTP_401_UNAUTHORIZED
            })