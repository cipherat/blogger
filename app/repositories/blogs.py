import csv
from typing import List, Dict, Any, Optional
import os

from app.utils.pagination import get_csv_row_count


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

    def find_by_permalink(self, permalink: str) -> Optional[Dict[str, Any]]:
        from app.models.blog import BlogModel
        #NOTE: This is inefficient for large datasets as it reads the entire CSV.
        for entry in self.get_all():
            try:
                temp_blog_model = BlogModel(**entry)
                if temp_blog_model.permalink_key == permalink:
                    return entry
            except Exception as e:
                continue
        return None

    def read_paged_blogs(self, page: int, limit: int) -> Dict[str, Any]:
        total_count = get_csv_row_count(self.file_path)
        
        start_index = (page - 1) * limit
        end_index = start_index + limit
        
        start_line = start_index + 2 
        end_line = end_index + 2

        paged_data: List[Dict[str, Any]] = []
        current_line = 1

        with open(self.file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, fieldnames=BLOG_FIELDNAMES)
            
            next(reader) 
            current_line += 1
            
            for row in reader:
                if current_line >= end_line:
                    break
                
                if current_line >= start_line:
                    paged_data.append(self._deserialize_row(row))
                    
                current_line += 1
                
        return {
            "blogs": paged_data,
            "total_count": total_count
        }
    
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
