import os
import sys
from sqlalchemy import create_engine, text, inspect

# Add root directory to sys.path so we can import 'database'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set env var before importing database
TEST_DB_URL = "sqlite:///migration_test.db"
os.environ["DATABASE_URL"] = TEST_DB_URL

# Now import database
import database
from database import init_db

def run_test():
    db_file = "migration_test.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    print(f"Using database: {TEST_DB_URL}")

    # Create a fresh engine for setup (bypassing database.py's global engine just in case)
    engine = create_engine(TEST_DB_URL)

    # 1. Create a partial schema (simulate old version)
    print("Creating partial schema (simulating old version)...")
    with engine.connect() as conn:
        # Create 'jobs' table with MINIMAL columns (id, type)
        # Missing: status, progress, video_id, etc.
        conn.execute(text("CREATE TABLE jobs (id VARCHAR(36) PRIMARY KEY, type VARCHAR(20));"))
        conn.commit()

    # Verify 'progress' is missing
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns('jobs')]
    if 'progress' in columns:
        print("ERROR: 'progress' column already exists! Test setup failed.")
        return

    print("Partial schema created. 'progress' column is missing.")

    # 2. Run init_db (the function we want to test)
    print("Running init_db()...")

    # Ensure database.py uses our test db
    database.engine = engine
    database.SessionLocal.configure(bind=engine)

    # Run the function
    init_db()

    # 3. Check if 'progress' exists now
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns('jobs')]

    if 'progress' in columns:
        print("SUCCESS: 'progress' column was added by init_db!")
    else:
        print("FAILURE: 'progress' column is still missing.")

if __name__ == "__main__":
    run_test()
