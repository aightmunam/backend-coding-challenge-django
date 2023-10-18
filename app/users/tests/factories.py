from django.contrib.auth.hashers import make_password

import factory
from factory.django import DjangoModelFactory
from faker import Faker

from users.models import User

faker = Faker()


class UserFactory(DjangoModelFactory):
    """User generation factory."""

    username = factory.Faker("name")
    password = factory.LazyFunction(lambda: make_password(faker.password(length=12)))

    class Meta:
        model = User
