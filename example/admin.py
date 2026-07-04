from django.contrib import admin

from example.models import ExampleItem


@admin.register(ExampleItem)
class ExampleItemAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
