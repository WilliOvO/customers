"""
Test Factory to make fake objects for testing
"""

import factory
from factory.fuzzy import FuzzyChoice
from service.models import Customer


class CustomerFactory(factory.Factory):
    """Creates fake customer"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Customer

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    password = factory.Faker("password")
    email = factory.Faker("email")
    address = factory.Faker("address")
    active = FuzzyChoice(choices=[True, False])


class BadCustomerFactory(factory.Factory):
    """Creates fake customer with bad attributes that do not adhere to the model"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Customer

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    password = factory.Faker("password")
    email = factory.Faker("email")
    address = factory.Faker("address")
    active = "not a boolean"  # should not work
