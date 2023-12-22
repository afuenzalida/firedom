from typing import (
    TYPE_CHECKING,
    Any,
    Self,
)
from google.cloud.firestore_v1.aggregation import AggregationQuery
from google.cloud.firestore_v1.query import Query as FirestoreQuery


if TYPE_CHECKING:
    from google.cloud.firestore_v1 import FieldFilter

    from model import Model


ASCENDING = 'ASCENDING'
DESCENDING = 'DESCENDING'


class Query(list):
    def __init__(
        self,
        records: list['Model'],
        model_class: type['Model'],
        query: FirestoreQuery = None,
    ) -> None:
        self.model_class = model_class
        self.query = query if query else self.model_class.collection.firestore_collection_ref
        super().__init__(records)

    def eval(self) -> Self:
        documents = self.query.stream()
        model_instances = []

        for document in documents:
            model_instance = self.model_class.from_db_dict(document.to_dict())
            model_instance._is_sync = True
            model_instances.append(model_instance)

        super().__init__(model_instances)

        return self

    def where(self, *filters: list['FieldFilter']) -> Self:
        for filter_ in filters:
            self.query = self.query.where(filter=filter_)

        self.eval()

        return self

    def order_by(self, field: str, desc: bool = False) -> Self:
        direction = DESCENDING if desc else ASCENDING

        self.query = self.query.order_by(field, direction=direction)
        self.eval()

        return self

    def limit(self, amount: int) -> Self:
        self.query = self.query.limit(amount)
        self.eval()

        return self

    def count(self) -> int:
        if isinstance(self.query, FirestoreQuery):
            aggregate_query = AggregationQuery(self.query)
        else:
            aggregate_query = self.query._aggregation_query()

        aggregate_query.count(alias='count')
        count_value = aggregate_query.get()[0][0].value

        return count_value

    def pluck(self, field_name: str) -> list[Any]:
        values = [getattr(record, field_name) for record in self]

        return values

    def delete(self) -> None:
        for record in self:
            record.delete()

    def __repr__(self) -> str:
        return f'Query({[str(record) for record in self]})'.replace("'", '')

    # Unused methods
    def append(self, *_) -> None:
        raise Exception("Results cannot be mutated manually.")

    def insert(self, *_) -> None:
        raise Exception("Results cannot be mutated manually.")

    def __add__(self, *_) -> None:
        raise Exception("Results cannot be mutated manually.")

    def __iadd__(self, *_) -> None:
        raise Exception("Results cannot be mutated manually.")
