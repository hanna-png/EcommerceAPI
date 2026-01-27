import factory
from faker import Faker

from ecommerceapi.models.product import Product
from tests.factories.category_factory import CategoryFactory

fake = Faker()


class ProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Product
        sqlalchemy_session_persistence = "flush"

    category = factory.SubFactory(CategoryFactory)
    name = factory.LazyFunction(lambda: fake.unique.word())
    description = factory.LazyFunction(lambda: fake.sentence(nb_words=12))
    price = factory.LazyFunction(
        lambda: round(fake.pyfloat(min_value=1, max_value=500, right_digits=2), 2)
    )
    sku = factory.LazyFunction(lambda: fake.unique.bothify(text="SKU-########"))
