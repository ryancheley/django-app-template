from django.urls import path

from example import views

app_name = "example"

urlpatterns = [
    path("", views.item_list, name="item_list"),
    path("items/count/", views.item_count, name="item_count"),
]
