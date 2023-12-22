import unittest

from dataclasses import dataclass
from uuid import uuid4

from firedom import Firedom
from firedom.collection import Collection
from firedom.query import Query


firedom = Firedom(service_account_json_path='firebase.json')


class UserQuery(Query):
    def with_pets(self) -> Query:
        return self.where(self.model_class.number_of_pets > 0)


class UserCollection(Collection):
    query_class = UserQuery

    def test_string(self) -> str:
        return 'test_string'

    def only_chileans(self) -> UserQuery:
        return self.where(self.model_class.country == 'Chile')


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

    def test_custom_collection(self) -> None:
        test_string = User.collection.test_string()
        assert test_string == 'test_string'

        only_chileans_query = User.collection.only_chileans()
        assert len(only_chileans_query) == 2

    def test_custom_query(self) -> None:
        with_pets_query = User.collection.all().with_pets()
        assert len(with_pets_query) == 2

    @classmethod
    def tearDownClass(cls) -> None:
        User.collection.all().delete()
