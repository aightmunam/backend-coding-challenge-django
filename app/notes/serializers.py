from django.db import transaction

from rest_framework import serializers

from .models import Note, Tag


class TagSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=30)

    class Meta:
        model = Tag
        fields = ["id", "title"]


class NoteSerializer(serializers.ModelSerializer):
    creator = serializers.CharField(default=serializers.CurrentUserDefault())
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Note
        fields = [
            "id", "title", "body", "tags", "creator", "is_public", "created_at",
            "last_modified_at",
        ]
        read_only_fields = ["creator"]

    @transaction.atomic
    def create(self, validated_data) -> Note:
        """Create a note and attach all the provided tags to it."""

        tags: list[dict] = validated_data.pop("tags", [])
        instance: Note = super().create(validated_data)
        if tags:
            instance.update_note_tags(tags)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data) -> Note:
        """Update a note and the tags attached to it."""

        tags: list[dict] | None = validated_data.pop("tags", None)
        instance: Note = super().update(instance, validated_data)
        if tags is not None:
            instance.update_note_tags(tags)
        return instance
