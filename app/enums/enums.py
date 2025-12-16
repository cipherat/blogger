from enum import Enum

class BlogState(Enum):
    """Corresponds to the 'state' field in your JSON example."""
    drafted = "drafted"
    published = "published"

    @classmethod
    def list_values(cls):
        return [state.value for state in cls]
