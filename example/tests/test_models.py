import pytest

from example.factories import ExampleItemFactory
from example.models import ExampleItem


@pytest.mark.django_db
def test_factory_creates_persisted_item() -> None:
    item = ExampleItemFactory()
    assert ExampleItem.objects.filter(pk=item.pk).exists()
    assert item.created_at is not None


@pytest.mark.django_db
def test_str_returns_name() -> None:
    item = ExampleItemFactory(name="A readable name")
    assert str(item) == "A readable name"


@pytest.mark.django_db
def test_default_ordering_is_newest_first() -> None:
    first = ExampleItemFactory()
    second = ExampleItemFactory()
    assert list(ExampleItem.objects.all()) == [second, first]
