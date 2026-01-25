import factory
from faker import Faker
from ecommerceapi.models.category import Category

fake = Faker()


class CategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Category
        sqlalchemy_session_persistence = "flush"

    name = factory.LazyFunction(lambda: fake.unique.word())
