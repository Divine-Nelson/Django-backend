from myapp.models import CustomUser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import CustomUserSerializer
from rest_framework.permissions import AllowAny


class SignupView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to access this endpoint

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
