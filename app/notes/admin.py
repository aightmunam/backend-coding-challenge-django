from django.contrib import admin

from .models import Note, Tag


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_filter = ["is_deleted"]
    list_select_related = ("creator",)
    search_fields = ["title"]
    list_display = ["title", "creator"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_display = ["title"]
