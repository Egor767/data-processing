from datetime import date
import random
from uuid import UUID, uuid4
from faker import Faker
import factory

from .models import UserRecord

fake = Faker()

ID_COLLISION_PROBA = 0.15
static_uuid = uuid4()
GENDER_CHOICES = ['male', 'female']
STATUS_CHOICES = ['new', 'active', 'deleted']
COUNTRY_CODES = ['RU', 'US', 'DE', 'GB', 'FR', 'JP', 'CN']


def get_static_uuid() -> UUID:
    print(f"Using static UUID for testing collisions: {static_uuid}")
    return static_uuid


class UserRecordFactory(factory.Factory):
    class Meta:
        model = UserRecord

    id = factory.LazyFunction(
        lambda: static_uuid if random.random() < ID_COLLISION_PROBA else uuid4()
    )

    name = factory.LazyFunction(
        lambda: fake.name() if random.random() > 0.15 else None
    )

    country = factory.LazyFunction(
        lambda: (
            random.choice(COUNTRY_CODES) if random.random() > 0.2
            else fake.country() if random.random() > 0.3
            else None
        )
    )

    city = factory.LazyFunction(
        lambda: fake.city() if random.random() > 0.25 else None
    )

    age = factory.LazyFunction(
        lambda: (
            random.randint(10, 100) if random.random() > 0.2
            else random.choice([-5, 150, 999]) if random.random() > 0.5
            else None
        )
    )

    gender = factory.LazyFunction(
        lambda: (
            random.choice(GENDER_CHOICES) if random.random() > 0.3
            else random.choice(['M', 'F', 'unknown', 'malee'])
        )
    )

    email = factory.LazyFunction(
        lambda: (
            fake.email() if random.random() > 0.25
            else None if random.random() > 0.5
            else f"invalid_{fake.word()}@{fake.domain_name()}"
        )
    )

    status = factory.LazyFunction(
        lambda: (
            random.choice(STATUS_CHOICES) if random.random() > 0.2
            else random.choice(['NEW', 'ACTIVE', 'inactive', 'blocked'])  # case/wrong
        )
    )

    value = factory.LazyFunction(
        lambda: random.choice([
            round(random.uniform(0, 1000), 2),
            -round(random.uniform(100, 500), 2),
            10_000
        ])
    )

    register_date = factory.LazyFunction(
        lambda: random.choice([
            fake.date_between(start_date="-2y", end_date="today"),
            None,
            fake.future_date(end_date="+1y"),
            date(1900, 1, 1)
        ])
    )


def get_dataset(n_rows: int = 200, use_static_uuid: bool = False) -> list[UserRecord]:
    if use_static_uuid:
        global static_uuid
        static_uuid = uuid4()

    return [UserRecordFactory() for _ in range(n_rows)]


if __name__ == "__main__":
    dataset = get_dataset(10)
    print(f"Generated {len(dataset)} rows")
    for i in range(len(dataset)):
        print(dataset[i].dict())
