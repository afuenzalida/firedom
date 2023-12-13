from google.cloud.firestore import Client as FirestoreClient

from .model import Model


class Firedom:
    def __init__(
        self,
        service_account_json_path: str | None = None,
        service_account_info: dict | None = None,
        firestore_client_instance: FirestoreClient | None = None,
    ) -> None:
        self.firestore_client: FirestoreClient = self.__get_firestore_client(
            service_account_json_path,
            service_account_info,
            firestore_client_instance,
        )
        self.Model: type[Model] = self.__get_model_class()

    def __get_firestore_client(
        self,
        service_account_json_path: str | None = None,
        service_account_info: dict | None = None,
        firestore_client_instance: FirestoreClient | None = None,
    ) -> FirestoreClient:
        firestore_client = None

        if firestore_client_instance:
            firestore_client = firestore_client_instance
        elif service_account_json_path:
            firestore_client = FirestoreClient.from_service_account_json(service_account_json_path)
        elif service_account_info:
            firestore_client = FirestoreClient.from_service_account_info(service_account_info)

        return firestore_client

    def __get_model_class(self) -> type[Model]:
        model_class = Model
        model_class._firestore_client = self.firestore_client

        return model_class
