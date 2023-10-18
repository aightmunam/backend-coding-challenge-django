import django_filters

from .models import Note


class CommaSeparatedCharFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    """Provide an `__in` lookup for comma separated strings."""

    pass


class CommaSeparatedUUIDFilter(django_filters.BaseInFilter, django_filters.UUIDFilter):
    """Provide an `__in` lookup for comma separated uuids."""

    pass


class NoteFilter(django_filters.FilterSet):
    """Filters for Note model."""

    tag_titles = CommaSeparatedCharFilter(field_name="tags__title", distinct=True)
    tag_ids = CommaSeparatedCharFilter(field_name="tags__id", distinct=True)
    ids = CommaSeparatedUUIDFilter(field_name="id")

    class Meta:
        model = Note
        fields = ["ids", "tag_titles", "tag_ids", "is_public"]
