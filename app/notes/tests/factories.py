import factory
from factory.django import DjangoModelFactory

from notes.models import Note, Tag
from users.tests.factories import UserFactory


class TagFactory(DjangoModelFactory):
    """Tag Generation Factory."""

    title = factory.Faker("name")

    class Meta:
        model = Tag


class NoteFactory(DjangoModelFactory):
    """Note generation factory."""

    title = factory.Faker("name")
    body = factory.Faker("sentence")
    creator = factory.SubFactory(UserFactory)

    class Meta:
        model = Note

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        """Add tags to the note object."""

        if extracted:
            for tag in extracted:
                self.tags.add(tag)
