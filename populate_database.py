import os
import random
from datetime import datetime, timedelta

from app.gateways.postgres.client import PostgresClient
from app.repositories.blog import BlogRepository
from app.models.blog import Blog
from app.models.dates import DatesModel
from app.enums.enums import BlogState

def seed_random_blogs():
    # 1. Setup the Infrastructure
    client = PostgresClient(
        dbname="blogger_db",
        user="blogger_user",
        password="your_password",
        host="database", 
        port=5432
    )
    repo = BlogRepository(client)
    model = Blog(repo)

    categories = ["Security", "Systems", "Web Dev", "Kernel", "Networking", "Cryptography"]
    topics = ["Linux", "Rust", "Postgres", "Docker", "FastAPI", "TCP/IP", "BGP", "Zero-Trust", "eBPF", "WASM"]
    
    tmp_dir = "/tmp/dummy_posts"
    os.makedirs(tmp_dir, exist_ok=True)

    print(f"--- Generating 5000 entries with full timestamps ---")

    for i in range(5000):
        topic = random.choice(topics)
        file_path = os.path.join(tmp_dir, f"post_{i}.md")
        
        with open(file_path, "w") as f:
            f.write(f"# {topic} Deep Dive\nContent for blog {i}...")

        # Randomize state
        state = random.choice([BlogState.PUBLISHED, BlogState.DRAFTED])
        
        # Generate full datetimes (not just dates)
        now = datetime.now()
        creation_dt = now - timedelta(days=random.randint(1, 365), hours=random.randint(0, 23))
        
        pub_date = None
        if state == BlogState.PUBLISHED:
            # Published slightly after creation
            pub_date = creation_dt + timedelta(hours=random.randint(1, 5))

        # ID based on high-res timestamp + index to force uniqueness
        unique_id = f"{int(now.timestamp())}{i}" 

        blog_data = model.Schema(
            id=unique_id,
            title=f"{random.choice(['The Art of', 'Deep Dive into', 'Hardening'])} {topic} {i}",
            category=random.choice(categories),
            keywords=[topic.lower(), "tech"],
            dates=DatesModel(
                created_at=creation_dt,
                published_at=pub_date,
                last_update=now
            ),
            content_file=file_path,
            references=[f"https://source.com/ref_{i}"],
            state=state.value
        )

        try:
            model.save(blog_data)
            if (i + 1) % 100 == 0:
                print(f"Seeded {i + 1} blogs...")
        except Exception as e:
            print(f"Error on blog {i}: {e}")

    client.close_all()
    print("--- Seeding Complete ---")

if __name__ == "__main__":
    seed_random_blogs()
