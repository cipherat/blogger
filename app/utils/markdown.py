import markdown2
import re
from functools import lru_cache


class MarkdownRenderer:
    @staticmethod
    def calculate_reading_time(raw_content: str) -> int:
        text_only = re.sub(r'[#*`\[\]\(\)-]', '', raw_content)
        words = text_only.split()
        word_count = len(words)
        
        minutes = round(word_count / 200)
        return max(1, minutes)
    
    @staticmethod
    @lru_cache(maxsize=100)
    def render(raw_content: str) -> str:
        html = markdown2.markdown(raw_content, extras=[
            "fenced-code-blocks",
            "code-friendly", 
            "tables",
            "header-ids",
            "metadata",
            "task_list",
            "break-on-newline",
        ])
        reading_time = MarkdownRenderer.calculate_reading_time(raw_content)
        word_count = len(raw_content.split())
        
        return {
            "html": html,
            "reading_time": reading_time,
            "word_count": word_count,
        }
