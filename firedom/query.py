from typing import (
    TYPE_CHECKING,
    Self,
)


if TYPE_CHECKING:
    from google.cloud.firestore_v1 import (
        FieldFilter,
        Query as FirestoreQuery,
    )

    from model import Model


ASCENDING = 'ASCENDING'
DESCENDING = 'DESCENDING'


class Query(list):
    def __init__(
        self,
        records: list['Model'],
        model_class: type['Model'],
        query: 'FirestoreQuery' = None,
    ) -> None:
        self._model_class = model_class
        self._query = query
        super().__init__(records)

    def eval(self) -> Self:
        if not self._query:
            self._query = self._model_class.collection.firestore_collection_ref

        documents = self._query.stream()
        model_instances = []

        for document in documents:
            model_instance = self._model_class.from_db_dict(document.to_dict())
            model_instance._is_sync = True
            model_instances.append(model_instance)

        super().__init__(model_instances)

        return self

    def where(self, *filters: list['FieldFilter']) -> Self:
        if not self._query:
            self._query = self._model_class.collection.firestore_collection_ref

        for filter_ in filters:
            self._query = self._query.where(filter=filter_)

        self.eval()

        return self

    def order_by(self, field: str, desc: bool = False) -> Self:
        direction = DESCENDING if desc else ASCENDING

        if not self._query:
            self._query = self._model_class.collection.firestore_collection_ref

        self._query = self._query.order_by(field, direction=direction)
        self.eval()

        return self

    def limit(self, amount: int) -> Self:
        if not self._query:
            self._query = self._model_class.collection.firestore_collection_ref

        self._query = self._query.limit(amount)
        self.eval()

        return self

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
