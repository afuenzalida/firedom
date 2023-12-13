import unittest

from dataclasses import dataclass
from firedom import Firedom
from uuid import uuid4


firedom = Firedom(service_account_json_path='firebase.json')


@dataclass
class User(firedom.Model):
    username: str
    country: str
    number_of_pets: int = 0

    class Config:
        document_id_field = 'username'
        collection_id = f'users-{uuid4()}'


records_to_create = [
    {
        'username': 'user_1',
        'country': 'Chile',
    },
    {
        'username': 'user_2',
        'country': 'Argentina',
        'number_of_pets': 2,
    },
    {
        'username': 'user_3',
        'country': 'Bolivia',
    },
    {
        'username': 'user_4',
        'country': 'Chile',
        'number_of_pets': 3,
    },
]


class TestModel(unittest.TestCase):
    def setUp(self) -> None:
        for record_data in records_to_create:
            User(**record_data).save()

    def test_where_query(self) -> None:
        records = User.collection.where(User.username == 'user_1')
        assert len(records) == 1

        records = User.collection.where(User.username == 'non_existing_user')
        assert len(records) == 0

        records = User.collection.where(User.username != 'non_existing_user')
        assert len(records) == len(records_to_create)

        records = User.collection.where(User.country == 'Chile')
        assert len(records) == 2

        records = User.collection.where(User.number_of_pets >= 2)
        assert len(records) == 2

        records = User.collection.where(User.number_of_pets > 2)
        assert len(records) == 1

        records = User.collection.where(User.number_of_pets <= 2)
        assert len(records) == 3

        records = User.collection.where(User.number_of_pets < 2)
        assert len(records) == 2

        records = User.collection.where(User.country.is_in(['Chile', 'Argentina']))
        assert len(records) == 3

        records = User.collection.where(User.country == 'Chile', User.number_of_pets == 3)
        assert len(records) == 1

    def test_limit_query(self) -> None:
        records = User.collection.all().limit(2)
        assert len(records) == 2

    @classmethod
    def tearDownClass(cls) -> None:
        User.collection.all().delete()
