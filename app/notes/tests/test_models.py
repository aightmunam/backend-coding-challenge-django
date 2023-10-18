from django.test import TestCase
from django.utils import timezone

from freezegun import freeze_time

from notes.models import Tag

from .factories import NoteFactory, TagFactory


class NoteModelTestCase(TestCase):
    def setUp(self):
        self.tag_foo = TagFactory(title="foo")
        self.tag_bar = TagFactory(title="bar")
        self.tag_foobar = TagFactory(title="foobar")

        self.note_one = NoteFactory(tags=(self.tag_foo, self.tag_foobar))
        self.note_two = NoteFactory(tags=(self.tag_bar, self.tag_foobar))

    def test_soft_delete(self):
        self.assertFalse(self.note_one.is_deleted)
        self.assertIsNone(self.note_one.deleted_at)

        yesterday = timezone.now() - timezone.timedelta(days=1)
        with freeze_time(yesterday):
            self.note_one.soft_delete()

        self.note_one.refresh_from_db()
        self.assertTrue(self.note_one.is_deleted)

        # deleted_at should be populated with correct time
        self.assertEqual(self.note_one.deleted_at, yesterday)

    def test_update_note_tags(self):
        tags_to_update = [
            {"title": "foobar"},
            {"title": "bar"},
            {"title": "helloworld"},
            {"title": "helloworld"},
        ]
        self.note_one.update_note_tags(tags_to_update)

        # Check that no duplicate tags are created for `foobar` and `bar`
        self.assertEqual(Tag.objects.count(), 4)

        # Check that self.note_two tags are unaffected
        self.assertSetEqual(
            set(self.note_two.tags.values_list("title", flat=True)),
            {"bar", "foobar"}
        )
