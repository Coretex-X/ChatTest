from django.contrib.auth.hashers import make_password
from rest_framework.generics import *
from rest_framework.views import *
from .models import *
from .serializer import Serializer
#from rest_framework_simplejwt.tokens import RefreshToken
from pydantic import BaseModel, EmailStr, Field, ConfigDict
#from django.contrib.auth.signals import user_login_failed  # NEW
from django.db.models import Q
# Create your views here.

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
            number:str = Field(min_length=8, max_length=23)
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
        
        
            
        
        
        
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class LoginView(APIView):                                                                                           
    def post(self, request):                                                                                        
#----------------------------------- Сбор даных ------------------------------------------------------------------------
        response_login = request.data.get('login')                                                                  
        response_password = request.data.get('password')

        class Validate(BaseModel):
            login:str=Field(min_length=3,max_length=40)
            password:str=Field(min_length=4,max_length=40)
            model_config=ConfigDict(extra='forbid')
        Validate(**request.data)

        try:
            queryset_login =  Models.objects.get(login=response_login)
        except Models.DoesNotExist:
            raise Http404({
                'meaning':'Такова пользователя несуществует',
                'status':status.HTTP_404_NOT_FOUND
                           })
        
        if queryset_login.check_password(response_password):
            #refresh = RefreshToken.for_user(queryset_login)
            #queryset_login.token = make_password(str(refresh))
            queryset_login.save()
            return Response({
                'name': response_login,
                'meaning':'Авторизация прошла успешно',
                'status':status.HTTP_201_CREATED
                })
        
        
        raise Http404({
                'meaning':'Неверный пороль',
                'status':status.HTTP_401_UNAUTHORIZED
            })
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////