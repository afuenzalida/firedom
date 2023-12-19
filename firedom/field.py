import dataclasses

from datetime import datetime
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from google.cloud.firestore_v1 import (
    And as FirestoreAnd,
    FieldFilter as FirestoreFieldFilter,
    Or as FirestoreOr,
)
from typing import (
    Any,
    TYPE_CHECKING,
    Union,
)


if TYPE_CHECKING:
    from firedom.model import Model


class Or(FirestoreOr):
    def __or__(self, value: Union['FieldFilter', 'And', 'Or']) -> 'Or':
        return Or(filters=[self, value])

    def __and__(self, value: Union['FieldFilter', 'And', 'Or']) -> 'And':
        return And(filters=[self, value])


class And(FirestoreAnd):
    def __or__(self, value: Union['FieldFilter', 'And', 'Or']) -> Or:
        return Or(filters=[self, value])

    def __and__(self, value: Union['FieldFilter', 'And', 'Or']) -> 'And':
        return And(filters=[self, value])


class FieldFilter(FirestoreFieldFilter):
    def __or__(self, value: Union['FieldFilter', 'And', 'Or']) -> Or:
        return Or(filters=[self, value])

    def __and__(self, value: Union['FieldFilter', 'And', 'Or']) -> And:
        return And(filters=[self, value])


class Field:
    def __init__(self, name: str, field_type: type, default_value: Any = None) -> None:
        self._name = name
        self.field_type = field_type
        self.default_value = default_value

    def __eq__(self, value: Any) -> FieldFilter:
        return FieldFilter(self._name, '==', value)

    def __ne__(self, value: Any) -> FieldFilter:
        return FieldFilter(self._name, '!=', value)

    def __lt__(self, value: Any) -> FieldFilter:
        return FieldFilter(self._name, '<', value)

    def __le__(self, value: Any) -> FieldFilter:
        return FieldFilter(self._name, '<=', value)

    def __gt__(self, value: Any) -> FieldFilter:
        return FieldFilter(self._name, '>', value)

    def __ge__(self, value: Any) -> FieldFilter:
        return FieldFilter(self._name, '>=', value)

    def __hash__(self) -> None:
        pass

    def is_in(self, values: list[Any]) -> FieldFilter:
        return FieldFilter(self._name, 'in', values)

    def is_not_in(self, values: list[Any]) -> FieldFilter:
        return FieldFilter(self._name, 'not-in', values)

    def to_db_value(self, value: Any) -> Any:
        return value

    def to_python_value(self, value: Any) -> Any:
        return value


class DatetimeField(Field):
    def to_python_value(self, value: DatetimeWithNanoseconds) -> datetime:
        return datetime.fromtimestamp(value.timestamp())


class RelatedField(Field):
    def to_db_value(self, value: 'Model') -> Any:
        return value.document_id

    def to_python_value(self, value: 'Model') -> Any:
        return self.field_type.collection.get(value)


class FieldFactory:
    FIELDS_MAPPING = {
        datetime: DatetimeField,
    }

    @classmethod
    def create_field(cls, **kwargs) -> Field:
        field_class = cls.FIELDS_MAPPING.get(kwargs.get('field_type'), Field)

        return field_class(**kwargs)

    @classmethod
    def generate_fields_definitions(cls, model_class: type['Model']) -> dict[str, Field]:
        fields_definitions = {}

        for name, field in model_class.__dataclass_fields__.items():
            if not field.kw_only:
                default_value = None

                if not isinstance(field.default, dataclasses._MISSING_TYPE):
                    default_value = field.default

                if any(parent_class.__name__ == 'Model' for parent_class in field.type.__bases__):
                    fields_definitions[name] = RelatedField(
                        name=name,
                        field_type=field.type,
                        default_value=default_value,
                    )
                else:
                    fields_definitions[name] = cls.create_field(
                        name=name,
                        field_type=field.type,
                        default_value=default_value,
                    )

        return fields_definitions
