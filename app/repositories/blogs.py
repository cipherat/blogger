import csv
from typing import List, Dict, Any, Optional
import os


BLOG_FIELDNAMES = [
    "id",
    "title",
    "category",
    "keywords",
    "created_at",
    "published_at",
    "last_update",
    "content_file",
    "references",
    "state"
]

class BlogRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=BLOG_FIELDNAMES)
                writer.writeheader()
            print(f"Created new database file: {self.file_path}")

    def _serialize_row(self, data: Dict[str, Any]) -> Dict[str, str]:
        row = data.copy()
        
        if 'dates' in row and isinstance(row['dates'], dict):
            row['created_at'] = row['dates'].get('created_at', '')
            row['published_at'] = row['dates'].get('published_at', '')
            row['last_update'] = row['dates'].get('last_update', '')
            del row['dates']

        # Pipe '|' is being used instead of commas ',' for CSV compatibility
        row['keywords'] = '|'.join(map(str, row.get('keywords', [])))
        row['references'] = '|'.join(map(str, row.get('references', [])))

        row['state'] = data['state'].value
        
        final_row = {field: str(row.get(field, '')) for field in BLOG_FIELDNAMES}
        return final_row

    def _deserialize_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        keywords = [k.strip() for k in row.get('keywords', '').split('|') if k.strip()]
        references = [r.strip() for r in row.get('references', '').split('|') if r.strip()]
        
        dates = {
            'created_at': row.get('created_at', ''),
            'published_at': row.get('published_at', ''),
            'last_update': row.get('last_update', ''),
        }

        metadata = {
            "id": row.get("id"),
            "title": row.get("title"),
            "category": row.get("category"),
            "keywords": keywords,
            "dates": dates,
            "content_file": row.get("content_file"),
            "references": references,
            "state": row.get("state"),
        }
        return metadata

    def get_all(self) -> List[Dict[str, Any]]:
        with open(self.file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return [self._deserialize_row(row) for row in reader]

    def find_by_id(self, blog_id: str) -> Optional[Dict[str, Any]]:
        for entry in self.get_all():
            if entry.get('id') == blog_id:
                return entry
        return None

    def add_blog(self, metadata: Dict[str, Any]) -> None:
        if not metadata.get('id'):
            # This logic should be placed in the service layer, but included here
            # for robustness when inserting.
            raise ValueError("Metadata must contain a unique 'id' field before insertion.")
        
        if self.find_by_id(metadata['id']):
            raise ValueError(f"Entry with ID '{metadata['id']}' already exists.")

        row_to_write = self._serialize_row(metadata)

        with open(self.file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=BLOG_FIELDNAMES)
            writer.writerow(row_to_write)


def get_blog_repository() -> BlogRepository:
    return BlogRepository(file_path=os.getenv("BLOGGER_DB", ".blogger/database.csv"))
