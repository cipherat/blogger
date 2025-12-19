import os
import random
from datetime import datetime, timedelta
from typing import List

from app.gateways.postgres.client import PostgresClient
from app.repositories.blog import BlogRepository
from app.models.blog import Blog
from app.models.dates import DatesModel
from app.enums.enums import BlogState


SUBJECTS = ["Memory management", "The borrow checker", "Interrupt handling", "BGP peering", "Cache invalidation", 
            "Vectorized instructions", "Zero-copy I/O", "Asymmetric encryption", "The Linux scheduler", "Garbage collection overhead"]
VERBS = ["leverages", "orchestrates", "mitigates", "abstracts", "serializes", "bottlenecks", "optimizes", "decouples", "encapsulates"]
OBJECTS = ["distributed state", "kernel space", "atomic operations", "user-land buffers", "the networking stack", 
           "side-channel attacks", "L3 cache hits", "concurrency primitives"]
CONNECTORS = ["Furthermore,", "In contrast,", "Consequently,", "From a systems perspective,", "Historically,", "Under heavy load,"]

def generate_random_paragraph(min_sentences=3, max_sentences=8):
    sentences = []
    for _ in range(random.randint(min_sentences, max_sentences)):
        s = f"{random.choice(CONNECTORS)} {random.choice(SUBJECTS)} {random.choice(VERBS)} {random.choice(OBJECTS)}."
        sentences.append(s)
    return " ".join(sentences)

def generate_devastating_markdown(topic, index):
    """Generates a high-entropy, long-form technical blog post."""
    content = [f"# {random.choice(['Demystifying', 'Refactoring', 'The Future of'])} {topic} {index}\n"]
    content.append(f"> [!IMPORTANT]\n> Automated performance test post. Word count: {random.randint(500, 1200)}.\n")
    
    for section in range(random.randint(4, 7)):
        content.append(f"## Section {section}: {random.choice(SUBJECTS)}")
        for _ in range(random.randint(1, 3)):
            content.append(generate_random_paragraph())
        if random.random() > 0.6:
            lang = random.choice(["rust", "python", "cpp", "bash"])
            content.append(f"```{lang}\n// Benchmarking {topic}\nwhile (executing) {{\n    {random.choice(VERBS)}_at_scale();\n}}\n```")
    
    return "\n\n".join(content)

def seed_random_blogs():
    client = PostgresClient(
        dbname="blogger_db",
        user="blogger_user",
        password="your_password",
        host="database",  # Change to "localhost" if running outside Docker
        port=5432
    )
    repo = BlogRepository(client)
    model = Blog(repo)

    categories = ["Security", "Systems", "Networking", "Kernel", "Cryptography"]
    topics = ["Rust", "eBPF", "Postgres", "WASM", "QUIC", "Linux", "Docker"]
    
    tmp_dir = "/tmp/dummy_posts"
    os.makedirs(tmp_dir, exist_ok=True)

    print(f"--- Generating 5000 high-entropy entries ---")

    for i in range(5000):
        topic = random.choice(topics)
        file_path = os.path.join(tmp_dir, f"post_{i}.md")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(generate_devastating_markdown(topic, i))

        state = random.choice([BlogState.PUBLISHED, BlogState.DRAFTED])
        now = datetime.now()
        creation_dt = now - timedelta(days=random.randint(1, 365))
        
        pub_date = creation_dt + timedelta(hours=2) if state == BlogState.PUBLISHED else None

        blog_data = model.Schema(
            id=f"{int(now.timestamp())}{i}",
            title=f"{random.choice(['Analysis of', 'Guide to', 'Internal:'])} {topic} {i}",
            category=random.choice(categories),
            keywords=[topic.lower(), "performance_test"],
            dates=DatesModel(
                created_at=creation_dt,
                published_at=pub_date,
                last_update=now
            ),
            content_file=file_path,
            references=[f"https://docs.local/ref_{i}"],
            state=state.value
        )

        try:
            model.save(blog_data)
            if (i + 1) % 100 == 0:
                print(f"Progress: {i + 1}/5000 seeded.")
        except Exception as e:
            print(f"Error on blog {i}: {e}")

    client.close_all()
    print("--- Seeding Complete ---")

if __name__ == "__main__":
    seed_random_blogs()
