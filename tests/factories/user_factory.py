import factory
from faker import Faker

from ecommerceapi.core.security import hash_password
from ecommerceapi.models.user import User

fake = Faker()


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "flush"

    email = factory.LazyFunction(lambda: fake.unique.email())
    hashed_password = factory.LazyFunction(lambda: hash_password("password123"))
    first_name = factory.LazyFunction(lambda: fake.first_name())
    last_name = factory.LazyFunction(lambda: fake.last_name())
