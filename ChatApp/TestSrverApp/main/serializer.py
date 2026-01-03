from rest_framework.serializers import *
from sign_up.models import Models

class Serializer(ModelSerializer):
    class Meta:
        model = Models
        fields = "__all__"

