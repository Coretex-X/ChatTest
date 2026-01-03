from django.http import HttpResponse
from rest_framework.generics import *
from rest_framework.views import *
from .serializer import Serializer
from sign_up.models import *
from .models import ModelsMain

# Create your views here.
class POST_Creat_Images(APIView):
    def post(self, requsts):
       logo = requsts.data.get('image')
       ModelsMain.objects.create(logo_image=logo)
       
       return Response('Ok') 