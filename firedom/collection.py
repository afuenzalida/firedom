from typing import (
    Any,
    Optional,
    Self,
    TYPE_CHECKING,
)

from google.cloud.firestore_v1.aggregation import AggregationQuery
from google.cloud.firestore_v1.query import Query as FirestoreQuery

from .utils import hybrid_method


if TYPE_CHECKING:
    from google.cloud.firestore_v1 import (
        CollectionReference,
        FieldFilter,
    )

    from model import Model


ASCENDING = 'ASCENDING'
DESCENDING = 'DESCENDING'


class Collection(list):
    model_class: type['Model'] = None
    collection_id: str = None

    def __init__(self, records: list['Model']) -> None:
        self.query = self.get_firestore_collection_ref()
        super().__init__(records)

    @classmethod
    def get_firestore_collection_ref(cls) -> 'CollectionReference':
        """
        Gets the reference of the current collection.
        """
        collection_ref = cls.model_class._firestore_client.collection(cls.collection_id)

        return collection_ref

    @classmethod
    def create(cls, **kwargs) -> 'Model':
        """
        Create a record with the fields and values received in the `kwargs`.
        """
        document = cls.model_class(**kwargs)
        document.save()

        return document

    @classmethod
    def all(cls) -> Self:
        """
        Gets all records in the collection.
        """
        class_instance = cls([])
        class_instance.eval()

        return class_instance

    @classmethod
    def get(cls, document_id: str) -> Optional['Model']:
        """
        Gets a record based on the document ID.
        """
        found_document = None

        document_ref = cls.get_firestore_collection_ref().document(document_id)
        document = document_ref.get()

        if document.exists:
            found_document = cls.model_class.from_db_dict(document.to_dict())
            found_document._is_sync = True

        return found_document

    @hybrid_method
    def where(self, *filters: list['FieldFilter']) -> Self:
        """
        Filters the documents in the collection or query based on the `filters` received.
        """
        for filter_ in filters:
            self.query = self.query.where(filter=filter_)

        self.eval()

        return self

    @hybrid_method
    def first(self) -> Optional['Model']:
        """
        Gets the first record in the collection or query.
        """
        if len(self):
            return self[0]

    @hybrid_method
    def last(self) -> Optional['Model']:
        """
        Gets the last record in the collection or query.
        """
        if len(self):
            return self[-1]

    def eval(self) -> Self:
        """
        Executes the query stored in the instance
        and transforms the documents into `Model` instances.
        """
        documents = self.query.stream()
        model_instances = []

        for document in documents:
            model_instance = self.model_class.from_db_dict(document.to_dict())
            model_instance._is_sync = True
            model_instances.append(model_instance)

        super().__init__(model_instances)

        return self

    def order_by(self, field: str, desc: bool = False) -> Self:
        """
        Sorts the documents in the collection or query based on `field`
        in ascending order (default) or descending order with `desc`.
        """
        direction = DESCENDING if desc else ASCENDING

        self.query = self.query.order_by(field, direction=direction)
        self.eval()

        return self

    def limit(self, amount: int) -> Self:
        """
        Limits documents in the collection based on `amount`.
        """
        self.query = self.query.limit(amount)
        self.eval()

        return self

    def count(self) -> int:
        """
        Count the documents in the collection or query.
        """
        if isinstance(self.query, FirestoreQuery):
            aggregate_query = AggregationQuery(self.query)
        else:
            aggregate_query = self.query._aggregation_query()

        aggregate_query.count(alias='count')
        count_value = aggregate_query.get()[0][0].value

        return count_value

    def pluck(self, field_name: str) -> list[Any]:
        """
        Gets the value of each document from the field specified in `field_name`.
        """
        values = [getattr(record, field_name) for record in self]

        return values

    def delete(self) -> None:
        """
        Removes documents from the current collection or query.
        """
        for record in self:
            record.delete()

    # Unused methods
    def append(self, *_) -> None:
        raise Exception("Results cannot be mutated manually.")

    def insert(self, *_) -> None:
        raise Exception("Results cannot be mutated manually.")

    def __add__(self, *_) -> None:
        raise Exception("Results cannot be mutated manually.")

    def __iadd__(self, *_) -> None:
        raise Exception("Results cannot be mutated manually.")
