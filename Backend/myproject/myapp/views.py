from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.urls import reverse
from .serializer import CustomUserSerializer, LoginForm
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken




class SignupView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to access this endpoint

    def post(self, request):
        email = request.data.get("email")
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate token and UID
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            email_subject = "Welcome"
            email_message = render_to_string('emails/welcome_email.txt', {
                'user': user,
            })

            # Send email
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email='your-email@gmail.com',
                recipient_list=[email],
                fail_silently=False,
            )
            return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        form = LoginForm(data=request.data)
        if form.is_valid():
            user = form.validated_data['user']
            login(request, user)  # Logs in the user

            # Generate token
            refresh = RefreshToken.for_user(user)

            # Get user initials
            first_name = user.first_name or ""
            last_name = user.last_name or ""
            initials = (first_name[0].upper() if first_name else "") + (last_name[0].upper() if last_name else "")

            return Response({
                "message": "Login Successful!",
                "token": str(refresh.access_token),
                "initials": initials,
            }, status=status.HTTP_200_OK)

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)




class CustomPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            
        except CustomUser.DoesNotExist:
            # Return a success-like message for security reasons
            return Response({"message": "If this email exists, a reset link has been sent."}, status=status.HTTP_200_OK)

        # Generate token and UID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = request.build_absolute_uri(
            reverse('reset_password_confirm', kwargs={'uidb64': uid, 'token': token})
        )
        email_subject = "Password Reset Request"
        email_message = render_to_string('emails/password_reset_email.txt', {
            'reset_link': reset_link,
            'user': user,
        })


        # Send email
        # Send email
        send_mail(
            subject=email_subject,
            message=email_message,
            from_email='your-email@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "If this email exists, a reset link has been sent."}, status=status.HTTP_200_OK)

class InitialsView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can fetch initials

    def get(self, request):
        user = request.user
        first_name = user.first_name or ""
        last_name = user.last_name or ""

        initials = (first_name[0].upper() if first_name else "") + (last_name[0].upper() if last_name else "")

        return Response({"initials": initials}, status=status.HTTP_200_OK)
