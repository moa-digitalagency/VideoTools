import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get("DATABASE_URL")

def migrate():
    if not DATABASE_URL:
        print("DATABASE_URL not set. Cannot run migration.")
        print("Please ensure DATABASE_URL is set in your environment variables.")
        return

    print(f"Connecting to database...")
    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as connection:
            print("Altering tiktok_downloads table...")
            # Using text() for raw SQL execution
            connection.execute(text("ALTER TABLE tiktok_downloads ALTER COLUMN title TYPE TEXT;"))
            connection.commit()
            print("Migration successful! 'title' column changed to TEXT.")

    except Exception as e:
        print(f"Migration failed: {e}")
        print("Note: This migration is intended for PostgreSQL. If you are using another database, the syntax might differ.")

if __name__ == "__main__":
    migrate()
