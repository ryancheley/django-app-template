import factory

from example.models import ExampleItem


class ExampleItemFactory(factory.django.DjangoModelFactory):
    """Sequence-based (not faker/random) so test data is deterministic,
    per Constitution Principle II."""

    class Meta:
        model = ExampleItem

    name = factory.Sequence(lambda n: f"Example item {n}")
    notes = ""
