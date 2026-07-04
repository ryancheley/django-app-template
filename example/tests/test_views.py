import pytest
from django.test import Client

from example.factories import ExampleItemFactory


@pytest.mark.django_db
def test_item_list_renders(client: Client) -> None:
    ExampleItemFactory(name="Visible item")
    response = client.get("/")
    assert response.status_code == 200
    assert b"Visible item" in response.content


@pytest.mark.django_db
def test_item_list_empty_state(client: Client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert b"No items yet" in response.content
