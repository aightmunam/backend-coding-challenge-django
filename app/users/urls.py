from django.urls import path

from rest_framework.authtoken import views

from .views import UserRegisterView

app_name = "users"


urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("token/", views.obtain_auth_token, name="token"),
]
