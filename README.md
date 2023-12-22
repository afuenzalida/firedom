# Firedom
[![Tests](https://github.com/afuenzalida/firedom/actions/workflows/python-test.yml/badge.svg?branch=main)](https://github.com/afuenzalida/firedom/actions/workflows/python-test.yml)


Simple Firestore ORM for Python.

## Installation

```shell
pip install firedom
```

## Getting started

#### Initialize Firedom

```python
from firedom import Firedom


firedom = Firedom(service_account_json_path='your-credentials.json')
```

#### Define your models

Create a model for your Firestore collection by inheriting from `Model`:

```python
from dataclasses import dataclass
from firedom import Firedom


firedom = Firedom(service_account_json_path='your-credentials.json')


@dataclass
class Company(firedom.Model):
    name: str


@dataclass
class User(firedom.Model):
    username: str
    email: int
    country: str
    city: str
    is_active: bool = True
    number_of_pets: int = 0
    company: Company

    class Config:
        # Required: Field to be used as document ID
        document_id_field = 'username'
```

## Manipulate documents

#### Create

```python
company = Company.collection.create(name='Example Company')

user = User.collection.create(
    username='afuenzalida',
    email='afuenzalida@example.com',
    country='Chile',
    city='Santiago',
    company=company,
)
```

#### Retrieve

```python
users = User.collection.all()

user = User.collection.get('afuenzalida')
```

#### Filter

```python
# All arguments are considered as AND:
users = User.collection.where(
    User.country == 'Chile',
    User.is_active == True,
    User.city.is_in(['Santiago', 'Valparaíso']),
    User.number_of_pets > 1,
)

# You can filter with OR using the | operator:
users = User.collection.where(
    (User.country == 'Chile') |
    (User.country == 'China'),
)

# And you can also filter explicitly with AND using the & operator:
users = User.collection.where(
    (User.city == 'Santiago') &
    (User.number_of_pets == 0),
)

# Full example: Filter by active users from Chile or China:
users = User.collection.where(
    (User.is_active == True) &
    (
        (User.country == 'Chile') |
        (User.country == 'China')
    ),
)
```

#### Sort

```python
users = User.collection.where(
    User.country == 'Chile',
).order_by(
    'email',
    desc=True,
)
```

#### Update

```python
user = User.collection.get('afuenzalida')
user.country = 'Australia'
user.save()
```

#### Delete

```python
user = User.collection.get('afuenzalida')
user.delete()

User.collection.all().delete()
```
