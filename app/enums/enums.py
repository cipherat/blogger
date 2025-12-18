from enum import Enum

class BlogState(Enum):
    DRAFTED = "drafted"
    PUBLISHED = "published"

    @classmethod
    def list_values(cls):
        return [state.value for state in cls]
