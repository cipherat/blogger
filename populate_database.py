import os
import time
from datetime import date, timedelta
from typing import List
import random
import sys

# --- 1. Import Application Components ---
from app.services.register_blog import RegisterBlogService
from app.contracts.register_blog import RegisterBlogRequest
from app.repositories.blogs import BlogRepository
from app.enums.enums import BlogState

# --- 2. Configuration ---
NUM_ENTRIES_TO_GENERATE = 5000
# NOTE: The explicit sleep needed to force file system timestamp updates.
SLEEP_PER_ENTRY = 1 # 5 milliseconds delay to avoid timestamp collision
BLOG_DB_PATH = ".blogger/database.csv" 
os.environ["BLOGGER_DB"] = BLOG_DB_PATH # Set the ENV for internal dependency resolution

# --- 3. Data Generation Helpers (No changes needed here) ---

def generate_random_data(index: int) -> RegisterBlogRequest:
    """Generates a semi-realistic, unique RegisterBlogRequest payload."""
    categories = ["Technology", "Science", "Finance", "Lifestyle", "Gaming", "Travel"]
    keywords_list = ["ai", "python", "fastapi", "testing", "database", "performance", "async", "csv"]
    states = [BlogState.published, BlogState.drafted]
    
    # 1. Create a truly unique file path for each run
    unique_marker = int(time.time() * 1000)
    content_file_path = f"/tmp/content_{unique_marker}_{index}.md"
    
    # Ensure the path exists and create the dummy file
    if not os.path.exists(os.path.dirname(content_file_path)):
        os.makedirs(os.path.dirname(content_file_path), exist_ok=True)
    with open(content_file_path, 'w') as f:
        f.write(f"Test content for entry {index}")
        
    # 2. Generate publication date
    start_date = date.today() - timedelta(days=365)
    random_days = random.randint(1, 365)
    pub_date = start_date + timedelta(days=random_days)
    
    selected_keywords = random.sample(keywords_list, k=random.randint(2, 4))

    # 3. Construct the RegisterBlogRequest
    return RegisterBlogRequest(
        title=f"Stress Test Blog Post #{index:04d}",
        category=random.choice(categories),
        keywords=selected_keywords,
        published_at=pub_date, 
        content_file=content_file_path,
        references=[f"/ref/doc_{random.randint(100, 999)}.pdf"],
        state=random.choice(states)
    )

# --- 4. Main Stress Test Execution ---

def run_stress_test():
    """Initializes the service and registers a large volume of data."""
    print("--- Starting Database Population Stress Test ---")
    
    # Manually ensure the database directory exists
    db_path_expanded = os.path.expanduser(BLOG_DB_PATH)
    if not os.path.exists(os.path.dirname(db_path_expanded)):
        os.makedirs(os.path.dirname(db_path_expanded), exist_ok=True)
    
    print(f"Target Database path: {db_path_expanded}")
    
    # Initialize the service (relies on os.environ["BLOGGER_DB"] being set)
    service = RegisterBlogService()
    
    start_time = time.time()
    successful_registrations = 0
    total_time_waited = 0

    print(f"Generating and registering {NUM_ENTRIES_TO_GENERATE} entries...")
    print(f"Delaying by {SLEEP_PER_ENTRY} seconds per entry to ensure unique creation timestamps...") # Log the delay

    for i in range(1, NUM_ENTRIES_TO_GENERATE + 1):
        try:
            # 1. GENERATE data and DUMMY file
            request_data = generate_random_data(i)
            
            # 2. FORCE TIME ADVANCEMENT BEFORE SERVICE RUN
            # This is the critical line to ensure the OS records a different ctime
            time.sleep(SLEEP_PER_ENTRY)
            total_time_waited += SLEEP_PER_ENTRY
            
            # 3. RUN service logic (creates metadata, saves to CSV)
            service.run(request_data) 
            
            # 4. CLEAN UP the dummy file
            os.remove(request_data.content_file)
            
            successful_registrations += 1
            
            if i % 500 == 0:
                print(f"  > Registered {i} entries...")

        except Exception as e:
            print(f"Error registering entry #{i}: {e.__class__.__name__}: {e}. Skipping.")
            # Ensure file cleanup even on error, if possible (though error is often on save)
            if os.path.exists(request_data.content_file):
                os.remove(request_data.content_file)
            continue

    end_time = time.time()
    
    # --- Results ---
    
    total_time = end_time - start_time
    
    # Re-initialize repository to get the actual count (could be slow)
    repository_check = BlogRepository(file_path=db_path_expanded) 
    total_entries = repository_check.get_all()
    
    print("\n--- Test Complete ---")
    print(f"Database Size (total entries): {len(total_entries)}")
    print(f"New Entries Registered: {successful_registrations}/{NUM_ENTRIES_TO_GENERATE}")
    print(f"Total Registration Time: {total_time:.2f} seconds (includes approx. {total_time_waited:.2f}s of forced delay)")
    
    if successful_registrations > 0:
        # Rate is now artificially slowed down by the sleep
        rate = successful_registrations / total_time
        print(f"Effective Registration Rate: {rate:.2f} entries/second")
    
    print("---------------------------------------------")

if __name__ == "__main__":
    if not os.path.exists("/tmp"):
        os.makedirs("/tmp", exist_ok=True)
        
    run_stress_test()
