from django.db.models import Q, QuerySet

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

from .filters import NoteFilter
from .models import Note
from .permissions import IsCreatorOrReadOnly
from .serializers import NoteSerializer


# TODO: Add swagger docs information for each endpoint separately.
class NoteViewSet(ModelViewSet):
    """API for handling creation, access and deletion of notes."""

    serializer_class = NoteSerializer
    permission_classes = [IsCreatorOrReadOnly]
    queryset = Note.active_objects.order_by("-created_at")
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = NoteFilter
    search_fields = ["title", "body"]
    ordering_fields = ["creator", "title", "is_public", "created_at", "last_modified_at"]

    def get_queryset(self) -> QuerySet[Note]:
        """
        Only fetch private notes that belong to the authenticated user.
        Public notes are visible to all users, even unauthenticated users.
        """

        qs: QuerySet = super().get_queryset().select_related("creator").prefetch_related("tags")
        query: Q = Q(is_public=True)
        if self.request.user.is_authenticated:
            query |= Q(creator_id=self.request.user.id)
        return qs.filter(query)

    def perform_destroy(self, instance: Note) -> None:
        """Soft delete note instead of removing it from the db."""

        instance.soft_delete()
