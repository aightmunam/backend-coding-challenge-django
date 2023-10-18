import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class ActiveNoteManager(models.Manager):
    """Manager to manage all the active (non-deleted) notes."""

    def get_queryset(self) -> models.QuerySet:
        """Filter out all the soft deleted notes."""

        return super().get_queryset().filter(is_deleted=False)


class Note(models.Model):
    """Represent a note with all the information including a creator user."""

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="notes", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=100)
    body = models.TextField()
    tags = models.ManyToManyField(to="notes.Tag", related_name="notes")
    is_public = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()
    active_objects = ActiveNoteManager()

    def __str__(self) -> str:
        return f"{self.title} - {self.created_at}"

    def update_note_tags(self, tags: list[dict] | set[dict]) -> None:
        """
        Set the given tags to the note. Any tags not included in the `tags` arg are
        removed from the instance.
        """

        selected_tags: set[Tag] = set()
        for tag in tags:
            selected_tag, _ = Tag.objects.get_or_create(**tag)
            selected_tags.add(selected_tag)
        self.tags.set(selected_tags)

    def soft_delete(self) -> None:
        """Soft delete and add the time of deletion."""

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()


class Tag(models.Model):
    """Represent a tag that may be linked to multiple Note objects."""

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    title = models.CharField(max_length=30, unique=True)

    def __str__(self) -> str:
        return self.title
