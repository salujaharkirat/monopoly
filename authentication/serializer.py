from django.contrib.auth.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True)

  class Meta:
    model = User
    fields = ['password', 'username', 'email']

  def create(self, validated_data):
    user = User.objects.create_user(
      username=validated_data["username"],
      password = validated_data["password"],
      email = validated_data.get("email", "")
    )

    return user

class LoginSerializer(serializers.Serializer):
  password = serializers.CharField(write_only=True)
  username = serializers.CharField(required=True)