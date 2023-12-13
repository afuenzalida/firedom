# Firedom
[![Run tests](https://github.com/afuenzalida/firedom/actions/workflows/python-test.yml/badge.svg)](https://github.com/afuenzalida/firedom/actions/workflows/python-test.yml)


Simple Firestore ORM for Python.

## Installation

```shell
pip install firedom
```

## Usage
Create an instance of the library's main class:

```python
firedom = Firedom(service_account_json_path='your-credentials.json')
```

Define the model of your collection by inheriting from the `Model` property of the instance you created:

```python
@dataclass  # <- Required
class User(firedom.Model):
    username: str
    email: int
    country: str
    city: str
    is_active: bool = True
    number_of_pets: int = 0

    class Config:
        # Required: Field to be used as document ID
        document_id_field = 'username'

        # Optional: Collection ID
        collection_id = 'users'
```

Manipulate the documents in your collection:

```python
# Get a document from the collection
user = User.collection.get('afuenzalida')

# Delete a document from the collection
user = User.collection.get('usuario_malvado')
user.delete()

# Get all documents in the collection
users = User.collection.all()

# Filter documents in the collection
users = User.collection.where(
    User.country == 'Chile',
    User.is_active == True,
    User.city.is_in(['Santiago', 'Valparaíso']),
    User.number_of_pets > 1,
)
```

Chain queries:

```python
# Sort the documents obtained in a query:
users = User.collection.where(
    User.country == 'Chile',
).order_by(
    'email',
    desc=True,
)

# Delete documents obtained in a query:
users = User.collection.all().delete()
```
