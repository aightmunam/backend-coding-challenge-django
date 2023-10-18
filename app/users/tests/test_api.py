from django.urls import reverse

from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from users.models import User

from .factories import UserFactory


class UserRegisterApiTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.faker = Faker()

    def test_register_new_user(self):
        request_body = {
            "username": self.faker.name(),
            "password": self.faker.password(),
            "password2": "something",
        }
        register_url = reverse("users:register")
        response = self.client.post(register_url, request_body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = response.json()
        self.assertIn("password", response)
        self.assertEqual(response["password"][0], "Password fields do not match.")

        request_body["password2"] = request_body["password"]
        response = self.client.post(register_url, request_body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        registered_user: User = User.objects.get(username=request_body["username"])
        self.assertTrue(registered_user.check_password(request_body["password"]))

    def test_register_duplicate_username(self):
        UserFactory(username="foobar")
        password = self.faker.password()
        request_body = {
            "username": "foobar",
            "password": password,
            "password2": password,
        }
        register_url = reverse("users:register")
        response = self.client.post(register_url, request_body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = response.json()
        self.assertIn("username", response)
        self.assertEqual(response["username"][0], "This field must be unique.")
