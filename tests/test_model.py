import unittest

from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime
from firedom import Firedom
from uuid import uuid4


firedom = Firedom(service_account_json_path='firebase.json')


@dataclass
class User(firedom.Model):
    username: str
    country: str
    number_of_pets: int = 0
    actions: list = field(default_factory=list)
    extra_data: dict = field(default_factory=dict)
    created_at: datetime = datetime.now()

    class Config:
        document_id_field = 'username'
        collection_id = f'users-{uuid4()}'


records_to_create = [
    {
        'username': 'user_1',
        'country': 'Perú',
    },
    {
        'username': 'user_2',
        'country': 'Argentina',
        'number_of_pets': 2,
    },
    {
        'username': 'user_3',
        'country': 'Bolivia',
        'actions': ['a', 'b'],
    },
    {
        'username': 'user_4',
        'country': 'Chile',
        'number_of_pets': 3,
        'actions': ['a', 'b'],
        'extra_data': {'id': 1, 'is_active': True},
    },
]


class TestModel(unittest.TestCase):
    def setUp(self) -> None:
        for record_data in records_to_create:
            User.collection.create(**record_data)

    def test_record_creation(self) -> None:
        records = User.collection.all()
        assert len(records_to_create) == len(records)

    def test_record_update(self) -> None:
        first_record = User.collection.first()
        first_record.country = 'Japón'
        first_record.save()
        first_record.refresh_from_db()

        assert first_record.country == 'Japón'

    def test_record_delete(self) -> None:
        first_record = User.collection.first()
        record_to_delete_id = first_record.username
        first_record.delete()

        records = User.collection.all()

        assert len(records_to_create) - 1 == len(records)

        deleted_record = User.collection.get(record_to_delete_id)

        assert deleted_record is None

    @classmethod
    def tearDownClass(cls) -> None:
        User.collection.all().delete()
