from typing import (
    Self,
    TYPE_CHECKING,
)

from .field import Field
from .query import Query


if TYPE_CHECKING:
    from google.cloud.firestore_v1 import (
        CollectionReference,
        FieldFilter,
    )

    from model import Model


class Collection:
    def __init__(
        self,
        model_class: type['Model'],
        fields: dict[str, Field],
        document_id_field: str,
        collection_id: str | None = None,
    ) -> None:
        self.model_class = model_class
        self.fields = fields
        self.document_id_field = document_id_field
        self.collection_id = (
            collection_id
            if collection_id
            else self.model_class.__name__.lower()
        )

    @property
    def firestore_collection_ref(self) -> 'CollectionReference':
        collection_ref = self.model_class._firestore_client.collection(self.collection_id)

        return collection_ref

    def get(self, document_id: str | int) -> Self | None:
        document_ref = self.firestore_collection_ref.document(document_id)
        document = document_ref.get()
        parsed_document = None

        if document.exists:
            parsed_document = self.model_class.from_db_dict(document.to_dict())
            parsed_document._is_sync = True

        return parsed_document

    def create(self, **kwargs) -> 'Model':
        document = self.model_class(**kwargs)
        document.save()

        return document

    def all(self) -> Query:
        query_result = Query([], self.model_class)
        query_result.eval()

        return query_result

    def where(self, *filters: list['FieldFilter']) -> Query:
        query_result = Query([], self.model_class)
        query_result.where(*filters)

        return query_result

    def first(self) -> 'Model':
        query_result = Query([], self.model_class)
        query_result.eval()

        if len(query_result):
            return query_result[0]

    def last(self) -> 'Model':
        query_result = Query([], self.model_class)
        query_result.eval()

        if len(query_result):
            return query_result[-1]
