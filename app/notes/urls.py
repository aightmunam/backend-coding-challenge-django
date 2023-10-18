from rest_framework.routers import SimpleRouter

from notes.views import NoteViewSet

app_name = "notes"
urlpatterns = []

router = SimpleRouter()
router.register("", NoteViewSet, basename="notes")

urlpatterns.extend(router.urls)
