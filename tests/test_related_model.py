import unittest

from dataclasses import dataclass
from firedom import Firedom
from uuid import uuid4


firedom = Firedom(service_account_json_path='firebase.json')


@dataclass
class Country(firedom.Model):
    name: str

    class Config:
        document_id_field = 'name'
        collection_id = f'countries-{uuid4()}'


@dataclass
class City(firedom.Model):
    name: str
    country: Country

    class Config:
        document_id_field = 'name'
        collection_id = f'cities-{uuid4()}'


class TestModel(unittest.TestCase):
    def test_related_model_creation(self) -> None:
        created_country = Country.collection.create(name='Chile')
        created_city = City.collection.create(name='Santiago', country=created_country)

        assert created_city.country == created_country

        obtained_country = Country.collection.get('Chile')
        obtained_city = City.collection.get('Santiago')

        assert isinstance(obtained_city.country, obtained_country.__class__)

    @classmethod
    def tearDownClass(cls) -> None:
        City.collection.all().delete()
        Country.collection.all().delete()
