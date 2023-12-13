import dataclasses

from typing import (
    TYPE_CHECKING,
    Self,
)

from .collection import Collection
from .field import (
    Field,
    FieldFactory,
    RelatedField,
)


if TYPE_CHECKING:
    from google.cloud.firestore_v1 import (
        Client as FirestoreClient,
        DocumentReference,
    )


@dataclasses.dataclass(repr=False, kw_only=True)
class Model:
    _is_sync: bool = False
    _firestore_client: 'FirestoreClient' = None

    collection: Collection = None

    class Config:
        document_id_field: str = None
        collection_id: str | int | None = None

    def __init_subclass__(cls) -> None:
        dataclasses.dataclass(cls)

        cls.__validate_document_id_field()

        fields_definition = cls.__get_fields_definition()
        cls.collection = cls.__build_collection_instance(fields_definition)
        cls.__set_fields(fields_definition)

        super().__init_subclass__()

    def __new__(cls, **kwargs) -> type['Model']:
        cls.__validate_field_values(kwargs)

        return super().__new__(cls)

    @classmethod
    def __build_collection_instance(cls, fields_definition: dict[str, Field]) -> Collection:
        collection_id = cls.__name__.lower()

        if hasattr(cls.Config, 'collection_id') and cls.Config.collection_id:
            collection_id = cls.Config.collection_id

        collection = Collection(
            cls,
            fields_definition,
            cls.Config.document_id_field,
            collection_id,
        )

        return collection

    @classmethod
    def __get_fields_definition(cls) -> None:
        parsed_fields = {}

        for name, field in cls.__dataclass_fields__.items():
            if not field.kw_only:
                default_value = None

                if not isinstance(field.default, dataclasses._MISSING_TYPE):
                    default_value = field.default

                if Model in field.type.__bases__:
                    parsed_fields[name] = RelatedField(
                        name=name,
                        field_type=field.type,
                        default_value=default_value,
                    )
                else:
                    parsed_fields[name] = FieldFactory.create_field(
                        name=name,
                        field_type=field.type,
                        default_value=default_value,
                    )

        return parsed_fields

    @classmethod
    def __set_fields(cls, fields_definition: dict[str, Field]) -> None:
        for name, field in fields_definition.items():
            setattr(cls, name, field)

    @classmethod
    def __validate_document_id_field(cls) -> None:
        if cls.Config.document_id_field not in cls.__dataclass_fields__.keys():
            raise ValueError(
                f"Document ID field \"{cls.Config.document_id_field}\" does not exist.",
            )
        document_id_field = cls.__dataclass_fields__[cls.Config.document_id_field]

        if document_id_field.type not in (str, int):
            raise TypeError(
                f"Document ID field value must be of type {str} or {int}. "
                f"Current type: {document_id_field.type}.",
            )

    @classmethod
    def __validate_field_values(cls, attributes: dict) -> None:
        for key, value in attributes.items():
            if key in cls.collection.fields.keys():
                expected_type = cls.collection.fields[key].field_type

                if type(value) is not expected_type:
                    raise TypeError(
                        f"Argument \"{key}\" must be of type {expected_type}. "
                        f"Current type: {type(value)}.",
                    )

    @property
    def document_id(self) -> str | int:
        return getattr(self, self.Config.document_id_field)

    @property
    def firestore_document_ref(self) -> 'DocumentReference':
        document_ref = self.__class__.collection.firestore_collection_ref.document(
            self.document_id,
        )

        return document_ref

    @classmethod
    def from_dict(cls, dict_: dict) -> Self:
        return cls(**dict_)

    @classmethod
    def from_db_dict(cls, dict_: dict) -> Self:
        fixed_dict = {
            key: cls.collection.fields[key].to_python_value(value)
            for key, value in dict_.items()
        }

        return cls(**fixed_dict)

    def to_dict(self) -> dict[str, any]:
        registered_fields = self.__class__.collection.fields

        registered_fields_values = {}

        for name, field in registered_fields.items():
            if hasattr(self, name):
                fixed_value = field.to_db_value(getattr(self, name))
            else:
                fixed_value = getattr(self, name, field.default_value)

            registered_fields_values[name] = fixed_value

        return registered_fields_values

    def save(self) -> Self:
        self.firestore_document_ref.set(self.to_dict())
        self._is_sync = True

    def delete(self) -> None:
        if self._is_sync:
            self.firestore_document_ref.delete()

    def refresh_from_db(self) -> None:
        document = self.firestore_document_ref.get()
        self.from_db_dict(document.to_dict())
        self._is_sync = True

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"({self.Config.document_id_field}={self.document_id})"
        )

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"({self.Config.document_id_field}={self.document_id})"
        )
