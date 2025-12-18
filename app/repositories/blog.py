from fastapi import Request
from typing import Any, Dict, List, Optional

from app.repositories.abstract import AbstractRepository

from app.gateways.postgres.client import PostgresClient
from app.enums.enums import BlogState


class BlogRepository(AbstractRepository):
    def __init__(self, db_client: PostgresClient):
        super().__init__(db_client)
        
    def _format_row(self, row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        
        data = dict(row)
        
        data['dates'] = {
            'created_at': data.pop('created_at'),
            'published_at': data.pop('published_at'),
            'last_update': data.pop('last_update')
        }
        return data

    def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        rows = self._call("fn_get_blog_by_id", (id, ))
        return self._format_row(rows[0]) if rows else None

    def get_page(self, page: int, limit: int, state: Optional[BlogState] = None) -> Dict[str, Any]:
        offset = (page - 1) * limit
        state_value = state.value if isinstance(state, BlogState) else None
        
        rows = self._call("fn_get_paged_blogs", (state_value, limit, offset))
        if not rows:
            return {"blogs": [], "total_count": 0}

        return {
            "blogs": [self._format_row(row) for row in rows],
            "total_count": rows[0]['total_count'],
        }

    def get_all(self) -> List[Dict[str, Any]]:
        rows = self._call("fn_get_all_blogs")
        return [self._format_row(row) for row in rows] if rows else []

    def add(self, metadata: Dict[str, Any]) -> None:
        dates = metadata.get('dates', {})
        state = metadata['state'].value if hasattr(metadata['state'], 'value') else metadata['state']
        
        params = (
            metadata['id'], metadata['title'], metadata['category'],
            metadata['keywords'], dates.get('created_at'),
            dates.get('published_at'), dates.get('last_update'),
            metadata['content_file'], metadata['references'], state,
        )
        self._call("fn_add_blog", params, commit=True)

    def update(self, id: str, metadata: Dict[str, Any]) -> None:
        dates = metadata.get('dates', {})
        state = metadata['state'].value if hasattr(metadata['state'], 'value') else metadata['state']
        
        params = (
            id, metadata['title'], metadata['category'],
            metadata['keywords'], dates.get('published_at'),
            metadata['content_file'], metadata['references'], state
        )
        self._call("fn_update_blog", params, commit=True)

    def delete(self, id: str) -> None:
        self._call("fn_delete_blog", (id, ), commit=True)

    def get_by_permalink(self, year: str, month: str, day: str, slug: str) -> Optional[Dict[str, Any]]:
        rows = self._call("fn_get_blog_by_permalink", (year, month, day, slug))
        return self._format_row(rows[0]) if rows else None


def get_blog_repository(request: Request) -> BlogRepository:
    db_client = request.app.state.db_client
    return BlogRepository(db_client)
