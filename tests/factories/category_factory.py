import factory
from faker import Faker

from ecommerceapi.models.category import Category

fake = Faker()


class CategoryFactory(factory.Factory):
    """Factory class to create Categories (ORM objects)"""

    class Meta:
        model = Category

    name = factory.LazyFunction(lambda: fake.unique.word())
