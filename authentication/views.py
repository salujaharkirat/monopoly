from django.shortcuts import render

from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_401_UNAUTHORIZED
from .serializer import RegisterSerializer, LoginSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
  serializer = RegisterSerializer(data = request.data)
  if serializer.is_valid(raise_exception=True):
    user = serializer.save() 
    token, created = Token.objects.get_or_create(user=user)
    # 3. Return the token to the frontend
    return Response({
        "token": token.key,
        "username": user.username,
        "message": "User registered successfully!"
    }, status=HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
  serializer = LoginSerializer(data = request.data)
  if serializer.is_valid(raise_exception=True):
    print(serializer.validated_data)
    user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
    print("user", user)
    if user:
      token, created = Token.objects.get_or_create(user=user)
      return Response({
        "token": token.key
      }, status = HTTP_200_OK)
    return Response({"message": "cannot login"}, status=HTTP_401_UNAUTHORIZED)
