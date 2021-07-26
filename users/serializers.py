from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    permission_classes = (IsAuthenticated, )
    class Meta:
        model = User
        exclude = ('password', )
        read_only_fields = ['username']
