from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
)


if TYPE_CHECKING:
    from .collection import Collection


class hybrid_method(classmethod):
    """
    Implementation of `classmethod` to instantiate the collection
    in case the method is called as a class method.
    """
    def __get__(
        self,
        instance: Optional['Collection'],
        collection_class: type['Collection'],
    ) -> Callable[..., Any] | Any:
        method = super().__get__ if instance is None else self.__func__.__get__

        if not instance:
            instance = collection_class([])
            instance.eval()
            collection_class = instance

        return method(instance, collection_class)
