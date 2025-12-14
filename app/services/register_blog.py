from typing import Dict

from app.contracts.register_blog import RegisterBlogRequest

class RegisterBlogService():
    def __init__(self):
        pass

    def run(self, request: RegisterBlogRequest) -> Dict:
        return {"request": request}

def get_register_blog_service() -> RegisterBlogService:
    return RegisterBlogService()
