import json
import uuid
import requests
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializer import CustomUserSerializer, LoginForm


class SignupView(APIView):
    """Handle user signup and send a welcome email."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            email_subject = "Welcome"
            email_message = render_to_string('emails/welcome_email.txt', {'user': user})

            send_mail(
                subject=email_subject,
                message=email_message,
                from_email='your-email@gmail.com',
                recipient_list=[email],
                fail_silently=False,
            )
            return Response({"message": 
                             "User created successfully!"}, 
                             status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Handle user login and generate JWT token."""
    permission_classes = [AllowAny]

    def post(self, request):
        form = LoginForm(data=request.data)
        if form.is_valid():
            user = form.validated_data['user']
            login(request, user)

            refresh = RefreshToken.for_user(user)
            first_name = user.first_name or ""
            last_name = user.last_name or ""
            initials = (
                first_name[0].upper() if first_name else "") + (last_name[0].upper() if last_name else "")

            return Response({
                "message": "Login Successful!",
                "token": str(refresh.access_token),
                "initials": initials,
            }, status=status.HTTP_200_OK)

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomPasswordResetView(APIView):
    """Handle password reset requests."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"message": "If this email exists, a reset link has been sent."}, status=status.HTTP_200_OK)

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

        send_mail(
            subject=email_subject,
            message=email_message,
            from_email='your-email@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "If this email exists, a reset link has been sent."}, status=status.HTTP_200_OK)


class UserDetailsView(APIView):
    """Retrieve details of the authenticated user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        first_name = user.first_name or ""
        last_name = user.last_name or ""
        email = user.email or ""

        initials = (first_name[0].upper() if first_name else "") + (last_name[0].upper() if last_name else "")
        full_name = f"{first_name} {last_name}".strip()

        return Response(
            {
                "initials": initials,
                "full_name": full_name,
                "email": email,
            },
            status=status.HTTP_200_OK,
        )


class PaymentView(APIView):
    """Handle payment requests via Swish API."""
    permission_classes = [AllowAny]
    SWISH_API_URL = "https://mss.cpc.getswish.net/swish-cpcapi/api/v2/paymentrequests"
    CERT_PATH = "/path/to/swish_certificate.pem"
    KEY_PATH = "/path/to/swish_key.pem"

    def post(self, request):
        amount = request.data.get("amount")
        message = request.data.get("message")
        payer_alias = request.data.get("payerAlias")

        instruction_uuid = str(uuid.uuid4())
        data = {
            "payeeAlias": "1234679304",
            "currency": "SEK",
            "callbackUrl": "http://192.168.0.75:8000/api/callback-payment/",
            "amount": amount,
            "message": message,
            "callbackIdentifier": str(uuid.uuid4()),
        }

        if payer_alias:
            data["payerAlias"] = payer_alias

        try:
            response = requests.put(
                f"{self.SWISH_API_URL}/{instruction_uuid}",
                json=data,
                cert=(self.CERT_PATH, self.KEY_PATH),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 201:
                return Response({
                    "id": instruction_uuid,
                    "token": response.headers.get("PaymentRequestToken")
                }, status=status.HTTP_201_CREATED)

            return Response({"error": response.json()}, status=response.status_code)

        except requests.exceptions.RequestException as error:
            return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CallBack(APIView):
    """Handle payment callback requests."""
    permission_classes = [AllowAny]

    @csrf_exempt
    @staticmethod
    @api_view(['POST'])
    def swish_callback(request):
        try:
            callback_data = json.loads(request.body)
            payment_status = callback_data.get("status")

            if payment_status == "PAID":
                pass  # Update your database logic here

            return JsonResponse({"status": "received"}, status=200)
        except json.JSONDecodeError as error:
            return JsonResponse({"error": str(error)}, status=500)
