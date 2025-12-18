from typing import Generic, TypeVar
from abc import ABC

T = TypeVar("T")

class AbstractModel(ABC, Generic[T]):
    def __init__(self, repository: T):
        self.repository = repository
