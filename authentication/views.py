from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication

from .serializer import RegisterSerializer

class LoginView(APIView):
    """Login and get token"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
      username = request.data.get('username')
      password = request.data.get('password')
      
      if not username or not password:
        return Response(
            {'detail': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
      user = authenticate(username=username, password=password)
      
      if not user:
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
      
      # Get or create token
      token, created = Token.objects.get_or_create(user=user)
      

      return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
      })

class RegisterView(APIView):
    """Register new user and get token"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
          user = serializer.save()
    
          # Create token
          token = Token.objects.create(user=user)
          
          return Response({
              'token': token.key,
              'user': {
                  'id': user.id,
                  'username': user.username,
                  'email': user.email,
              }
          }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """Logout - delete token"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
      # Delete the user's token
      try:
          request.user.auth_token.delete()
      except:
          pass
      
      return Response(
          {'detail': 'Successfully logged out'},
          status=status.HTTP_200_OK
      )

class GetCurrentUserView(APIView):
    """Get current user info"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
      user = request.user
      
      return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
      })
