from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignupView, LoginView
from .views import CustomPasswordResetView


urlpatterns = [
    path('signup/', SignupView.as_view(), name="signup"),
    path('login/', LoginView.as_view(), name="login"),
    path('reset_password/', CustomPasswordResetView.as_view(), name="reset_password"),
    path(
    'reset/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(template_name="emails/reset_password_form.html"),
    name="reset_password_confirm"
),

    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(template_name="emails/password_reset_done.html"), name="password_reset_complete"),
]
