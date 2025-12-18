from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from app.gateways.postgres.client import PostgresClient


class AbstractRepository(ABC):
    def __init__(self, client: PostgresClient):
        self.client = client

    def _call(self, func_name: str, params: Tuple = (), commit: bool = False):
        return self.client.call_function(func_name, params, commit)

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_page(self, page: int, limit: int, **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_all(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def add(self, data: Any) -> None:
        pass

    @abstractmethod
    def update(self, id: int, data: Any) -> None:
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        pass
