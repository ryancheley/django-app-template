from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from example.models import ExampleItem


def item_list(request: HttpRequest) -> HttpResponse:
    items = ExampleItem.objects.all()
    return render(request, "example/item_list.html", {"items": items})
