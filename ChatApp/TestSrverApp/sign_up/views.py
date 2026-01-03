from django.contrib.auth.hashers import make_password
from rest_framework.generics import *
from rest_framework.views import *
from .models import *
from .serializer import Serializer
from rest_framework_simplejwt.tokens import RefreshToken
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from axes.handlers.proxy import AxesProxyHandler
from axes.helpers import get_client_ip_address
from django.contrib.auth.signals import user_login_failed  # NEW
from django.db.models import Q
# Create your views here.

class RegistrationView(CreateAPIView):
    serializer_class = Serializer

    def post(self, request):
        response_login = request.data.get('login')
        response_email = request.data.get('email')
        response_password = request.data.get('password')

        class Validate(BaseModel):
            login:str = Field(min_length=3,max_length=40)
            email:EmailStr = Field(min_length=3,max_length=50)
            password:str = Field(min_length=4,max_length=40)
            model_config=ConfigDict(extra='forbid') 
        Validate(**request.data)

        response_password = make_password(response_password)
        Models.objects.create(
            login=response_login, 
            email=response_email, 
            password=response_password
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
            refresh = RefreshToken.for_user(queryset_login)
            queryset_login.token = make_password(str(refresh))
            queryset_login.save()
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'name': response_login,
                'meaning':'Авторизация прошла успешно',
                'status':status.HTTP_201_CREATED
                })
        
        
        raise Http404({
                'meaning':'Неверный пороль',
                'status':status.HTTP_401_UNAUTHORIZED
            })
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////