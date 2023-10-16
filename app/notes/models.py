import uuid

from django.conf import settings
from django.db import models


class ActiveNoteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Note(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notes", on_delete=models.CASCADE)
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

    def __str__(self):
        return f"{self.title} - {self.created_at}"


class Tag(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    title = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.title
