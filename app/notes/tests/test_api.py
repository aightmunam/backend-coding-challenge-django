from django.contrib.auth import get_user_model

from faker import Faker
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from notes.models import Note

from .factories import NoteFactory, TagFactory


class BaseNotesAPITestCase(APITestCase):
    def setUp(self):
        self.faker = Faker()
        self.user = get_user_model().objects.create(
            username=self.faker.name(), password=self.faker.password()
        )
        self.other_user = get_user_model().objects.create(
            username=self.faker.name(), password=self.faker.password()
        )
        self.other_user_token = Token.objects.create(user=self.other_user)

        self.user_token = Token.objects.create(user=self.user)

        self.client = APIClient()
        self.client.credentials(**{"HTTP_AUTHORIZATION": f"Token {self.user_token.key}"})


class NotesCreateAPITestCase(BaseNotesAPITestCase):
    def test_create_note_for_authenticated_user(self):
        request_body = {
            "title": self.faker.name(),
            "body": self.faker.sentence(),
            "tags": [
                {
                    "title": self.faker.name()
                }
            ]
        }
        response = self.client.post(reverse("notes:notes-list"), request_body, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = response.json()

        self.assertIn("id", response)
        self.assertIn("title", response)
        self.assertIn("body", response)
        self.assertIn("creator", response)
        self.assertIn("tags", response)
        self.assertIn("created_at", response)
        self.assertIn("last_modified_at", response)

        created_note = Note.objects.get(id=response["id"])
        self.assertEqual(created_note.title, request_body["title"])
        self.assertEqual(created_note.body, request_body["body"])
        self.assertEqual(created_note.creator, self.user)
        added_tags = created_note.tags.all()
        self.assertEqual(len(added_tags), 1)
        self.assertEqual(added_tags[0].title, request_body["tags"][0]["title"])

    def test_create_note_for_unauthenticated_user(self):
        request_body = {
            "title": self.faker.name(),
            "body": self.faker.sentence(),
            "tags": [
                {
                    "title": self.faker.name()
                }
            ]
        }
        self.client.credentials(**{})
        response = self.client.post(reverse("notes:notes-list"), request_body, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class NotesListAPITestCase(BaseNotesAPITestCase):
    def test_list_notes_for_unauthenticated_user(self):
        NoteFactory.create_batch(3, is_public=False, creator=self.user)
        public_notes = NoteFactory.create_batch(5, is_public=True, creator=self.user)

        self.client.credentials(**{})
        response = self.client.get(reverse("notes:notes-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = response.json()
        self.assertEqual(response["count"], 5)

        notes_ids_in_response = {note["id"] for note in response["results"]}

        self.assertSetEqual(notes_ids_in_response, {str(note.id) for note in public_notes})

    def test_list_notes_for_authenticated_user(self):
        owned_notes = NoteFactory.create_batch(
            3, is_public=False, creator=self.user
        )
        other_user_notes = NoteFactory.create_batch(
            2, is_public=False, creator=self.other_user
        )
        other_user_public_notes = NoteFactory.create_batch(
            2, is_public=True, creator=self.other_user
        )
        owned_public_notes = NoteFactory.create_batch(
            3, is_public=True, creator=self.other_user
        )

        response = self.client.get(reverse("notes:notes-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = response.json()
        self.assertEqual(response["count"], 8)
        note_response = response["results"][0]
        self.assertIn("id", note_response)
        self.assertIn("title", note_response)
        self.assertIn("body", note_response)
        self.assertIn("creator", note_response)
        self.assertIn("tags", note_response)
        self.assertIn("created_at", note_response)
        self.assertIn("last_modified_at", note_response)

        # self.user should be able to access all public notes and only their own private notes
        notes_ids_in_response = {note["id"] for note in response["results"]}
        required_notes = owned_notes + other_user_public_notes + owned_public_notes
        for note in required_notes:
            self.assertIn(str(note.id), notes_ids_in_response)

        for note in other_user_notes:
            self.assertNotIn(str(note.id), notes_ids_in_response)

    def test_list_notes_queries(self):
        tags = TagFactory.create_batch(10)
        NoteFactory.create_batch(
            10, is_public=False, creator=self.user, tags=tags
        )

        # There should be no n+1 issue. There should be 4 queries in total:
        # 1. fetch user (auth)
        # 2. count of the queryset objects for pagination
        # 3. fetch all notes
        # 4. Query to prefetch tags for all the notes fetched in query 3
        with self.assertNumQueries(4):
            response = self.client.get(reverse("notes:notes-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_notes_filter_by_tags(self):
        tag_foo = TagFactory(title="foo")
        tag_bar = TagFactory(title="bar")
        tag_foobar = TagFactory(title="foobar")

        notes_with_foo = NoteFactory.create_batch(
            2, creator=self.user, tags=(tag_foo,)
        )
        notes_with_foo_foobar = NoteFactory.create_batch(
            1, creator=self.user, tags=(tag_foo, tag_foobar)
        )
        notes_with_bar = NoteFactory.create_batch(
            3, creator=self.user, tags=(tag_bar,)
        )
        notes_with_bar_foobar = NoteFactory.create_batch(
            1, creator=self.user, tags=(tag_bar, tag_foobar)
        )

        response = self.client.get(reverse("notes:notes-list"), {"tag_titles": "foo"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = response.json()
        self.assertEqual(response["count"], 3)
        response_notes = {note["id"] for note in response["results"]}
        expected_notes = notes_with_foo + notes_with_foo_foobar
        for note in expected_notes:
            self.assertIn(str(note.id), response_notes)

        response = self.client.get(reverse("notes:notes-list"), {"tag_titles": "foo,foobar"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = response.json()
        self.assertEqual(response["count"], 4)
        response_notes = {note["id"] for note in response["results"]}
        expected_notes = notes_with_foo + notes_with_foo_foobar + notes_with_bar_foobar
        for note in expected_notes:
            self.assertIn(str(note.id), response_notes)

        response = self.client.get(reverse("notes:notes-list"), {"tag_titles": "bar,foobar"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = response.json()
        self.assertEqual(response["count"], 5)
        response_notes = {note["id"] for note in response["results"]}
        expected_notes = notes_with_bar + notes_with_foo_foobar + notes_with_bar_foobar
        for note in expected_notes:
            self.assertIn(str(note.id), response_notes)

        response = self.client.get(
            reverse("notes:notes-list"), {"tag_ids": f"{str(tag_foobar.id)}"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = response.json()
        self.assertEqual(response["count"], 2)
        response_notes = {note["id"] for note in response["results"]}
        expected_notes = notes_with_foo_foobar + notes_with_bar_foobar
        for note in expected_notes:
            self.assertIn(str(note.id), response_notes)

    def test_list_notes_search_by_content(self):
        foo_note = NoteFactory(
            title="foo with some random text",
            body="This is a random note",
            creator=self.user
        )
        bar_note = NoteFactory(
            title="bar with some dummy text",
            body="This is a dummy note",
            creator=self.user
        )

        # the search keyword "foo" is found in foo_note title
        response = self.client.get(reverse("notes:notes-list"), {"search": "foo"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = response.json()
        self.assertEqual(response["count"], 1)
        response_note = response["results"][0]
        self.assertEqual(response_note["id"], str(foo_note.id))

        # the search keyword "random" is found in `foo_note` body
        response = self.client.get(reverse("notes:notes-list"), {"search": "random"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = response.json()
        self.assertEqual(response["count"], 1)
        response_note = response["results"][0]
        self.assertEqual(response_note["id"], str(foo_note.id))

        # the search keyword "dummy" is found in `bar_note` body
        response = self.client.get(reverse("notes:notes-list"), {"search": "dummy"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = response.json()
        self.assertEqual(response["count"], 1)
        response_note = response["results"][0]
        self.assertEqual(response_note["id"], str(bar_note.id))

        # the search keyword "note" is found in both notes' body
        response = self.client.get(reverse("notes:notes-list"), {"search": "note"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = response.json()
        self.assertEqual(response["count"], 2)
        response_notes = {note["id"] for note in response["results"]}
        self.assertIn(str(foo_note.id), response_notes)
        self.assertIn(str(bar_note.id), response_notes)


class NotesRetrieveTestCase(BaseNotesAPITestCase):
    def test_note_retrieve_access(self):
        note = NoteFactory(creator=self.user, is_public=True)
        note_detail_url = reverse("notes:notes-detail", kwargs={"pk": note.pk})

        # public notes can be accessible by unauthenticated users, and other users
        self.client.credentials(*{})
        response = self.client.get(note_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(**{"HTTP_AUTHORIZATION": f"Token {self.other_user_token.key}"})
        response = self.client.get(note_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # If the note is private, access is only limited to the creator
        note.is_public = False
        note.save()
        response = self.client.get(note_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.credentials(**{"HTTP_AUTHORIZATION": f"Token {self.user_token.key}"})
        response = self.client.get(note_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NoteDeleteAPITestCase(BaseNotesAPITestCase):
    def test_delete_created_note(self):
        note = NoteFactory(creator=self.user)
        self.assertFalse(note.is_deleted)
        self.assertIsNone(note.deleted_at)
        note_detail_url = reverse("notes:notes-detail", kwargs={"pk": note.pk})
        response = self.client.delete(note_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check soft deletion
        note.refresh_from_db()
        self.assertTrue(note.is_deleted)
        self.assertIsNotNone(note.deleted_at)

        # Soft deleted note should not be accessible
        response = self.client.get(note_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_created_note(self):
        # If note is public, the user will still be able to read it,
        # but delete request should be forbidden (403)
        note = NoteFactory(creator=self.other_user, is_public=True)
        note_detail_url = reverse("notes:notes-detail", kwargs={"pk": note.pk})
        response = self.client.delete(note_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # If note is private, non-creator user will get 404
        note = NoteFactory(creator=self.other_user, is_public=False)
        note_detail_url = reverse("notes:notes-detail", kwargs={"pk": note.pk})
        response = self.client.delete(note_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class NotesUpdateAPITestCase(BaseNotesAPITestCase):
    def test_update_created_note(self):
        old_tags = TagFactory.create_batch(2)
        note = NoteFactory(creator=self.user, tags=old_tags)
        note_detail_url = reverse("notes:notes-detail", kwargs={"pk": note.pk})

        request_body = {
            "title": self.faker.name(),
            "body": self.faker.sentence(),
            "tags": [
                {
                    "title": self.faker.word()
                },
                {
                    "title": self.faker.word()
                },
                {
                    "title": self.faker.word()
                }
            ]
        }
        response = self.client.patch(note_detail_url, request_body, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = response.json()
        self.assertIn("id", response)
        self.assertIn("title", response)
        self.assertIn("body", response)
        self.assertIn("creator", response)
        self.assertIn("tags", response)
        self.assertIn("created_at", response)
        self.assertIn("last_modified_at", response)

        self.assertEqual(len(response["tags"]), 3)
        tags_in_response = {tag["title"] for tag in response["tags"]}
        for tag in request_body["tags"]:
            self.assertIn(tag["title"], tags_in_response)

        for tag in old_tags:
            self.assertNotIn(tag.title, tags_in_response)

        # Check if the changes have been persisted to the db
        note.refresh_from_db()

        self.assertEqual(note.title, request_body["title"])
        self.assertEqual(note.body, request_body["body"])
        note_tags = note.tags.values_list("title", flat=True)
        self.assertEqual(len(request_body["tags"]), len(note_tags))
        for tag in request_body["tags"]:
            self.assertIn(tag["title"], note_tags)

    def test_update_non_created_note(self):
        request_body = {
            "title": self.faker.name()
        }

        # If note is public, other users will still be able to read it,
        # but update request should be forbidden (403)
        note = NoteFactory(creator=self.other_user, is_public=True)
        note_detail_url = reverse("notes:notes-detail", kwargs={"pk": note.pk})
        response = self.client.patch(note_detail_url, request_body, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # If note is private, non-creator users will not have any access, should receive 404
        note = NoteFactory(creator=self.other_user, is_public=False)
        note_detail_url = reverse("notes:notes-detail", kwargs={"pk": note.pk})
        response = self.client.patch(note_detail_url, request_body, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
