import unittest

from dataclasses import dataclass
from uuid import uuid4

from firedom import Firedom
from firedom.collection import Collection
from firedom.utils import hybrid_method


firedom = Firedom(service_account_json_path='firebase.json')


class UserCollection(Collection):
    @classmethod
    def second(cls) -> str:
        return cls.all()[1]

    @hybrid_method
    def without_pets(self) -> Collection:
        return self.where(self.model_class.number_of_pets == 0)

    def set_country(self, country: str) -> None:
        for record in self:
            record.country = country
            record.save()


@dataclass
class User(firedom.Model):
    username: str
    country: str
    number_of_pets: int = 0

    collection_class = UserCollection

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


class TestCustomQueryAndCollection(unittest.TestCase):
    def setUp(self) -> None:
        for record_data in records_to_create:
            User(**record_data).save()

    def test_class_method(self) -> None:
        second_record = User.collection.second()
        assert second_record.username == records_to_create[1]['username']

    def test_hybrid_method(self) -> None:
        users_with_pets = User.collection.without_pets()
        assert len(users_with_pets) == 2

        users_with_pets_from_chile = User.collection.where(
            User.country == 'Chile',
        ).without_pets()
        assert len(users_with_pets_from_chile) == 1

    def test_instance_method(self) -> None:
        users = User.collection.where(User.country == 'Chile')
        users.set_country('Brasil')

        for user in users:
            assert user.country == 'Brasil'

    @classmethod
    def tearDownClass(cls) -> None:
        User.collection.all().delete()
