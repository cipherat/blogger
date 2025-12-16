import re

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text) # Remove non-alphanumeric chars (except space/hyphen)
    text = re.sub(r'[-\s]+', '-', text).strip('-') # Collapse spaces/hyphens to a single hyphen
    return text
